import os, uuid, json, logging
from datetime import datetime
from agents import (
    Runner,
    gen_trace_id,
    trace,
    InputGuardrailTripwireTriggered,
    OutputGuardrailTripwireTriggered,
    TResponseInputItem,
    RunItem,
    ModelResponse,
)
from my_agents.classification_agent import classification_agent
from my_agents.non_relevance_agent import non_relevance_agent
from my_agents.low_complexity_response_agent import low_complexity_response_agent
from my_agents.high_complexity_response_agent import high_complexity_response_agent
from my_agents.quality_assurance_agent import quality_assurance_agent
from utils.fetch_user import fetch_user
from utils.map_costs import map_costs
from typing import List, Optional
from schemas.enums import Flag
from schemas.types import (
    QueryContext,
    QueryResponse,
    Query,
    QualityScore,
    User,
    FailedResponse,
    Usages,
)


MAX_RETRIES = 3
TIMEOUT_LIMIT = 180
CERTAINTY_THRESHOLD = 0.5


class QueryResolver:
    def __init__(self, query: Query):
        self.query = query
        self.trace_id = gen_trace_id()
        self.thread_id = str(uuid.uuid4())

        self.query_user_profile: Optional[User] = None
        self.query_context: Optional[QueryContext] = None

        self.failed_responses: List[FailedResponse] = []
        self.response: Optional[str] = None
        self.flag: Optional[Flag] = Flag.OK
        self.score: Optional[int] = None
        self.run_items: List[RunItem] = []
        self.input_items: List[TResponseInputItem] = [
            {"content": self.query.body, "role": "user"}
        ]

        self._start_time: Optional[datetime] = None
        self._end_time: Optional[datetime] = None

        self.usages: List[Usages] = []
        self.total_tokens: int = 0
        self.cost_estimate: float = 0.0

    async def run(self):
        with trace("App user query", trace_id=self.trace_id):
            self._start_time = datetime.now()

            try:
                self.query_user_profile = await fetch_user(self.query.sender)
                self.query_context = await self._classify_query()

                if self.query_context.certainty.score < CERTAINTY_THRESHOLD:
                    logging.info(
                        "\nUnclear query, requires human response\n", exc_info=True
                    )
                    self.flag = Flag.UNDETERMINED
                    return

                await self._response_loop()

            except InputGuardrailTripwireTriggered as e:
                self.flag = Flag.UNRELEVANT
                self.response = await self._generate_non_relevance_response()

            except OutputGuardrailTripwireTriggered as e:
                logging.info(
                    f"Model output flagged as inadequate... {e}", exc_info=True
                )
                self.flag = Flag.INADEQUATE

            except Exception as e:
                logging.error(f"Something else went wrong... {e}", exc_info=True)
                self.flag = Flag.ERROR

            finally:
                self._end_time = datetime.now()
                return await self._finalize_response()

    async def _response_loop(self):
        start_time = datetime.now()

        while (datetime.now() - start_time).total_seconds() <= TIMEOUT_LIMIT:
            if len(self.failed_responses) >= MAX_RETRIES:
                self._use_best_failed_response()
                break

            response = await self._generate_response(self.input_items)

            self.input_items.append(
                {"content": response.final_output, "role": "assistant"}
            )

            evaluator_result = await self._evaluate_response(self.input_items)

            if (
                evaluator_result.score_tag == "pass"
                or evaluator_result.score_tag == "fail"
            ):
                self.response = response.final_output
                self.score = evaluator_result.score_number
                if evaluator_result.score_tag == "fail":
                    self.flag = Flag.INADEQUATE
                break

            self._record_failure(response.final_output, evaluator_result)
        else:
            logging.warning("Response loop timed out.")
            self.flag = Flag.TIMEOUT

    async def _classify_query(self):
        classification = await Runner.run(
            classification_agent, self.query.body, context=self.query_user_profile
        )
        self._add_usage(classification.raw_responses, classification.last_agent.name)

        return QueryContext(
            certainty=classification.final_output.certainty,
            complexity=classification.final_output.complexity,
            sentiment=classification.final_output.sentiment,
            user=self.query_user_profile,
            category=classification.final_output.category,
        )

    async def _generate_response(self, input_items: List[TResponseInputItem]):
        agent_to_use = (
            high_complexity_response_agent
            if isinstance(self.query_context, QueryContext)
            and self.query_context.complexity.score > 0.5
            else low_complexity_response_agent
        )

        result = await Runner.run(
            agent_to_use,
            input_items,
            context=self.query_context,
        )

        self.run_items.extend(result.new_items)
        self._add_usage(result.raw_responses, result.last_agent.name)
        return result

    async def _evaluate_response(
        self, input_items: list[TResponseInputItem]
    ) -> QualityScore:
        evaluator_result = await Runner.run(quality_assurance_agent, input_items)
        self._add_usage(
            evaluator_result.raw_responses, evaluator_result.last_agent.name
        )
        return evaluator_result.final_output

    async def _generate_non_relevance_response(self):
        result = await Runner.run(
            non_relevance_agent,
            self.query.body,
            context=self.query_user_profile,
        )
        self._add_usage(result.raw_responses, result.last_agent.name)

        return result.final_output

    async def _store_response(self, response: QueryResponse):
        os.makedirs("outputs", exist_ok=True)

        with open(
            f"outputs/output_{datetime.now().strftime('%Y-%m-%dT%H-%M-%S')}.json",
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                response.to_serializable_dict(), file, ensure_ascii=False, indent=4
            )

    def _add_usage(self, responses: list[ModelResponse], agent: str):
        for response in responses:
            usage = response.usage

            costs = map_costs(usage, agent)

            self.usages.append(
                Usages(
                    agent=agent,
                    requests=usage.requests,
                    input_tokens=usage.input_tokens,
                    output_tokens=usage.output_tokens,
                    total_tokens=usage.total_tokens,
                    cost_estimate=costs,
                )
            )
            self.total_tokens += usage.total_tokens
            self.cost_estimate += costs

    def _use_best_failed_response(self):
        best = max(self.failed_responses, key=lambda r: r.score_number)
        self.response = best.text
        self.score = best.score_number
        self.flag = Flag.INADEQUATE

    def _record_failure(self, response_text: str, evaluation: QualityScore):
        retry = len(self.failed_responses) + 1
        self.failed_responses.append(
            FailedResponse(
                retry,
                response_text,
                evaluation.score_tag,
                evaluation.score_number,
                evaluation.feedback,
            )
        )
        self.input_items.append(
            {"content": f"Feedback: {evaluation.feedback}", "role": "system"}
        )

    async def _finalize_response(self):
        final_response = QueryResponse(
            trace_id=self.trace_id,
            trace_link=f"https://platform.openai.com/traces/trace?trace_id={self.trace_id}",
            created_at=datetime.now().isoformat(sep="_", timespec="seconds"),
            duration=str(
                self._end_time - self._start_time
                if self._end_time and self._start_time
                else 0
            ),
            user_profile=self.query_user_profile,
            query=self.query,
            response_flag=self.flag.value if self.flag else None,
            response_score=self.score,
            response=self.response,
            failed_responses=self.failed_responses,
            input_items=self.input_items,
            run_items=[
                {"agent": item.agent.name, "output": item.to_input_item()}
                for item in self.run_items
            ],
            usages=self.usages,
            total_tokens=self.total_tokens,
            cost_estimate=self.cost_estimate,
        )

        if isinstance(self.query_context, QueryContext):
            final_response.category = self.query_context.category
            final_response.sentiment = self.query_context.sentiment
            final_response.certainty = self.query_context.certainty
            final_response.complexity = self.query_context.complexity

        await self._store_response(final_response)
        return final_response.to_serializable_dict()
