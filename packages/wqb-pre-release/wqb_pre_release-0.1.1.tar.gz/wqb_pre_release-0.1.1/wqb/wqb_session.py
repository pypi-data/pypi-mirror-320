import asyncio
import itertools
from collections.abc import Awaitable, Coroutine, Generator, Iterable
from requests import Response
from requests.auth import HTTPBasicAuth
from . import (
    GET,
    POST,
    LOCATION,
    RETRY_AFTER,
    EQUITY,
    Alpha,
    MultiAlpha,
    Region,
    Delay,
    Universe,
    InstrumentType,
    Category,
    FieldType,
    DatasetsOrder,
    FieldsOrder,
    Status,
    AlphaType,
    Language,
    Color,
    Neutralization,
    UnitHandling,
    NanHandling,
    Pasteurization,
    AlphasOrder,
)
from .auto_auth_session import AutoAuthSession
from .filter_range import FilterRange
from .wqb_urls import (
    URL_ALPHAS_ALPHAID,
    URL_ALPHAS_ALPHAID_CHECK,
    URL_AUTHENTICATION,
    URL_DATAFIELDS,
    URL_DATAFIELDS_FIELDID,
    URL_DATASETS,
    URL_DATASETS_DATASETID,
    URL_OPERATORS,
    URL_SIMULATIONS,
    URL_USERS_SELF_ALPHAS,
)

__all__ = ['WQBSession', 'concurrent_await']


async def concurrent_await(
    awaitables: Iterable[Awaitable[object]],
    *,
    concurrency: int | asyncio.Semaphore | None = None,
    return_exceptions: bool = False,
) -> Coroutine[None, None, list[object | BaseException]]:
    if concurrency is None:
        return await asyncio.gather(*awaitables)
    if isinstance(concurrency, int):
        concurrency = asyncio.Semaphore(value=concurrency)

    async def semaphore_wrapper(
        awaitable: Awaitable[object],
    ) -> Coroutine[None, None, object]:
        async with concurrency:
            result = await awaitable
        return result

    return await asyncio.gather(
        *(semaphore_wrapper(awaitable) for awaitable in awaitables),
        return_exceptions=return_exceptions,
    )


def to_multi_alphas(
    alphas: Iterable[Alpha],
    multiple: int | Iterable[object],
) -> Generator[MultiAlpha, None, None]:
    alphas = iter(alphas)
    multiple = range(multiple) if isinstance(multiple, int) else tuple(multiple)
    try:
        while True:
            multi_alpha = []
            for _ in multiple:
                multi_alpha.append(next(alphas))
            yield multi_alpha
    except StopIteration as e:
        if 0 < len(multi_alpha):
            yield multi_alpha


class WQBSession(AutoAuthSession):

    def __init__(
        self,
        wqb_auth: tuple[str, str] | HTTPBasicAuth,
        **kwargs,
    ) -> None:
        if not isinstance(wqb_auth, HTTPBasicAuth):
            wqb_auth = HTTPBasicAuth(*wqb_auth)
        super().__init__(
            POST,
            URL_AUTHENTICATION,
            auth_expected=lambda resp: 201 == resp.status_code,
            expected=lambda resp: resp.status_code not in (204, 401, 429),
            auth=wqb_auth,
            **kwargs,
        )

    @property
    def wqb_auth(
        self,
    ) -> HTTPBasicAuth:
        return self.kwargs['auth']

    @wqb_auth.setter
    def wqb_auth(
        self,
        wqb_auth: tuple[str, str] | HTTPBasicAuth,
    ) -> None:
        if not isinstance(wqb_auth, HTTPBasicAuth):
            wqb_auth = HTTPBasicAuth(*wqb_auth)
        self.kwargs['auth'] = wqb_auth

    async def retry(
        self,
        method: str,
        url: str,
        *args,
        max_tries: int | Iterable[object] = itertools.repeat(None),
        max_key_errors: int = 1,
        max_value_errors: int = 1,
        delay_key_error: float = 2.0,
        delay_value_error: float = 2.0,
        **kwargs,
    ) -> Coroutine[None, None, Response | None]:
        tries = 0
        resp = None
        key_errors = 0
        value_errors = 0
        for tries, _ in enumerate(
            range(max_tries) if isinstance(max_tries, int) else max_tries, start=1
        ):
            resp = self.request(method, url, *args, **kwargs)
            try:
                await asyncio.sleep(float(resp.headers[RETRY_AFTER]))
            except KeyError as e:
                key_errors += 1
                if max_key_errors <= key_errors:
                    break
                await asyncio.sleep(delay_key_error)
            except ValueError as e:
                value_errors += 1
                if max_value_errors <= value_errors:
                    break
                await asyncio.sleep(delay_value_error)
        else:
            self.logger.warning(
                '\n'.join(
                    (
                        f"{self}.{'retry'} (max {tries} tries ran out)",
                        f"The last response {resp}:",
                        f"    status_code = {resp.status_code}",
                        f"    reason = {resp.reason}",
                        f"    url = {resp.url}",
                        f"    elapsed = {resp.elapsed}",
                        f"    headers = {resp.headers}",
                        f"    text = {resp.text}",
                    )
                )
            )
        return resp

    async def simulate(
        self,
        target: Alpha | MultiAlpha,
        *args,
        **kwargs,
    ) -> Coroutine[None, None, Response | None]:
        return await self.retry(
            GET,
            self.post(
                URL_SIMULATIONS,
                json=target,
                max_tries=60,
                delay_unexpected=10.0,
            ).headers[LOCATION],
            *args,
            **kwargs,
        )

    async def concurrent_simulate(
        self,
        targets: Iterable[Alpha | MultiAlpha],
        concurrency: int | asyncio.Semaphore,
        *args,
        return_exceptions: bool = False,
        **kwargs,
    ) -> Coroutine[None, None, list[Response | BaseException]]:
        if isinstance(concurrency, int):
            concurrency = asyncio.Semaphore(value=concurrency)
        return await concurrent_await(
            (self.simulate(target, *args, **kwargs) for target in targets),
            concurrency=concurrency,
            return_exceptions=return_exceptions,
        )

    async def check(
        self,
        alpha_id: str,
        *args,
        **kwargs,
    ) -> Coroutine[None, None, Response | None]:
        return await self.retry(
            GET,
            URL_ALPHAS_ALPHAID_CHECK.format(alpha_id),
            *args,
            **kwargs,
        )

    async def concurrent_check(
        self,
        alpha_ids: Iterable[str],
        concurrency: int | asyncio.Semaphore,
        *args,
        return_exceptions: bool = False,
        **kwargs,
    ) -> Coroutine[None, None, list[Response | BaseException]]:
        if isinstance(concurrency, int):
            concurrency = asyncio.Semaphore(value=concurrency)
        return await concurrent_await(
            (self.check(alpha_id, *args, **kwargs) for alpha_id in alpha_ids),
            concurrency=concurrency,
            return_exceptions=return_exceptions,
        )

    def get_authentication(
        self,
        *args,
        **kwargs,
    ) -> Response:
        return self.get(URL_AUTHENTICATION, *args, **kwargs)

    def post_authentication(
        self,
        *args,
        **kwargs,
    ) -> Response:
        return self.post(URL_AUTHENTICATION, *args, auth=self.wqb_auth, **kwargs)

    def delete_authentication(
        self,
        *args,
        **kwargs,
    ) -> Response:
        return self.delete(URL_AUTHENTICATION, *args, **kwargs)

    def head_authentication(
        self,
        *args,
        **kwargs,
    ) -> Response:
        return self.head(URL_AUTHENTICATION, *args, **kwargs)

    def search_opeators(
        self,
        *args,
        **kwargs,
    ) -> Response:
        return self.get(URL_OPERATORS, *args, **kwargs)

    def locate_dataset(
        self,
        dataset_id: str,
        *args,
        **kwargs,
    ) -> Response:
        return self.get(URL_DATASETS_DATASETID.format(dataset_id), *args, **kwargs)

    def search_datasets_limited(
        self,
        region: Region,
        delay: Delay,
        universe: Universe,
        *args,
        instrument_type: InstrumentType = EQUITY,
        search: str | None = None,
        category: Category | None = None,
        theme: bool | None = None,
        coverage: FilterRange | None = None,
        value_score: FilterRange | None = None,
        alpha_count: FilterRange | None = None,
        user_count: FilterRange | None = None,
        order: DatasetsOrder | None = None,
        limit: int = 50,
        offset: int = 0,
        others: Iterable[str] | None = None,
        **kwargs,
    ) -> Response:
        limit = min(max(limit, 1), 50)
        offset = min(max(offset, 0), 10000 - limit)
        params = [
            f"region={region}",
            f"delay={delay}",
            f"universe={universe}",
        ]
        params.append(f"instrumentType={instrument_type}")
        if search is not None:
            params.append(f"search={search}")
        if category is not None:
            params.append(f"category={category}")
        if theme is not None:
            params.append(f"theme={'true' if theme else 'false'}")
        if coverage is not None:
            params.append(coverage.to_params('coverage'))
        if value_score is not None:
            params.append(value_score.to_params('valueScore'))
        if alpha_count is not None:
            params.append(alpha_count.to_params('alphaCount'))
        if user_count is not None:
            params.append(user_count.to_params('userCount'))
        if order is not None:
            params.append(f"order={order}")
        params.append(f"limit={limit}")
        params.append(f"offset={offset}")
        params.extend(others)
        return self.get(URL_DATASETS + '?' + '&'.join(params), *args, **kwargs)

    def search_datasets(
        self,
        region: Region,
        delay: Delay,
        universe: Universe,
        *args,
        limit: int = 50,
        offset: int = 0,
        **kwargs,
    ) -> Generator[Response, None, None]:
        return (
            self.search_datasets_limited(
                region, delay, universe, *args, limit=limit, offset=offset, **kwargs
            )
            for offset in range(
                offset,
                self.search_datasets_limited(
                    region, delay, universe, *args, limit=1, offset=offset, **kwargs
                ).json()['count'],
                limit,
            )
        )

    def locate_field(
        self,
        field_id: str,
        *args,
        **kwargs,
    ) -> Response:
        return self.get(URL_DATAFIELDS_FIELDID.format(field_id), *args, **kwargs)

    def search_fields_limited(
        self,
        region: Region,
        delay: Delay,
        universe: Universe,
        *args,
        instrument_type: InstrumentType = EQUITY,
        dataset_id: str | None = None,
        search: str | None = None,
        category: Category | None = None,
        theme: bool | None = None,
        coverage: FilterRange | None = None,
        type: FieldType | None = None,
        alpha_count: FilterRange | None = None,
        user_count: FilterRange | None = None,
        order: FieldsOrder | None = None,
        limit: int = 50,
        offset: int = 0,
        others: Iterable[str] | None = None,
        **kwargs,
    ) -> Response:
        limit = min(max(limit, 1), 50)
        offset = min(max(offset, 0), 10000 - limit)
        params = [
            f"region={region}",
            f"delay={delay}",
            f"universe={universe}",
        ]
        params.append(f"instrumentType={instrument_type}")
        if dataset_id is not None:
            params.append(f"dataset.id={dataset_id}")
        if search is not None:
            params.append(f"search={search}")
        if category is not None:
            params.append(f"category={category}")
        if theme is not None:
            params.append(f"theme={'true' if theme else 'false'}")
        if coverage is not None:
            params.append(coverage.to_params('coverage'))
        if type is not None:
            params.append(f"type={type}")
        if alpha_count is not None:
            params.append(alpha_count.to_params('alphaCount'))
        if user_count is not None:
            params.append(user_count.to_params('userCount'))
        if order is not None:
            params.append(f"order={order}")
        params.append(f"limit={limit}")
        params.append(f"offset={offset}")
        params.extend(others)
        return self.get(URL_DATAFIELDS + '?' + '&'.join(params), *args, **kwargs)

    def search_fields(
        self,
        region: Region,
        delay: Delay,
        universe: Universe,
        *args,
        limit: int = 50,
        offset: int = 0,
        **kwargs,
    ) -> Generator[Response, None, None]:
        return (
            self.search_fields_limited(
                region, delay, universe, *args, limit=limit, offset=offset, **kwargs
            )
            for offset in range(
                offset,
                self.search_fields_limited(
                    region, delay, universe, *args, limit=1, offset=offset, **kwargs
                ).json()['count'],
                limit,
            )
        )

    def locate_alpha(
        self,
        alpha_id: str,
        *args,
        **kwargs,
    ) -> Response:
        return self.get(URL_ALPHAS_ALPHAID.format(alpha_id), *args, **kwargs)

    def filter_alphas_limited(
        self,
        *args,
        name: str | None = None,
        competition: bool | None = None,
        type: AlphaType | None = None,
        language: Language | None = None,
        date_created: FilterRange | None = None,
        favorite: bool | None = None,
        date_submitted: FilterRange | None = None,
        start_date: FilterRange | None = None,
        status: Status | None = None,
        category: Category | None = None,
        color: Color | None = None,
        tag: str | None = None,
        hidden: bool | None = None,
        region: Region | None = None,
        instrument_type: InstrumentType | None = None,
        universe: Universe | None = None,
        delay: Delay | None = None,
        decay: FilterRange | None = None,
        neutralization: Neutralization | None = None,
        truncation: FilterRange | None = None,
        unit_handling: UnitHandling | None = None,
        nan_handling: NanHandling | None = None,
        pasteurization: Pasteurization | None = None,
        sharpe: FilterRange | None = None,
        returns: FilterRange | None = None,
        pnl: FilterRange | None = None,
        turnover: FilterRange | None = None,
        drawdown: FilterRange | None = None,
        margin: FilterRange | None = None,
        fitness: FilterRange | None = None,
        book_size: FilterRange | None = None,
        long_count: FilterRange | None = None,
        short_count: FilterRange | None = None,
        sharpe60: FilterRange | None = None,
        sharpe125: FilterRange | None = None,
        sharpe250: FilterRange | None = None,
        sharpe500: FilterRange | None = None,
        os_is_sharpe_ratio: FilterRange | None = None,
        pre_close_sharpe: FilterRange | None = None,
        pre_close_sharpe_ratio: FilterRange | None = None,
        self_correlation: FilterRange | None = None,
        prod_correlation: FilterRange | None = None,
        order: AlphasOrder | None = None,
        limit: int = 100,
        offset: int = 0,
        others: Iterable[str] | None = None,
        **kwargs,
    ) -> Response:
        limit = min(max(limit, 1), 100)
        offset = min(max(offset, 0), 10000 - limit)
        params = []
        if name is not None:
            params.append(f"name{name if name[0] in '~=' else '~' + name}")
        if competition is not None:
            params.append(f"competition={'true' if competition else 'false'}")
        if type is not None:
            params.append(f"type={type}")
        if language is not None:
            params.append(f"settings.language={language}")
        if date_created is not None:
            params.append(date_created.to_params('dateCreated'))
        if favorite is not None:
            params.append(f"favorite={'true' if favorite else 'false'}")
        if date_submitted is not None:
            params.append(date_submitted.to_params('dateSubmitted'))
        if start_date is not None:
            params.append(start_date.to_params('os.startDate'))
        if status is not None:
            params.append(f"status={status}")
        if category is not None:
            params.append(f"category={category}")
        if color is not None:
            params.append(f"color={color}")
        if tag is not None:
            params.append(f"tag={tag}")
        if hidden is not None:
            params.append(f"hidden={'true' if hidden else 'false'}")
        if region is not None:
            params.append(f"settings.region={region}")
        if instrument_type is not None:
            params.append(f"settings.instrumentType={instrument_type}")
        if universe is not None:
            params.append(f"settings.universe={universe}")
        if delay is not None:
            params.append(f"settings.delay={delay}")
        if decay is not None:
            params.append(decay.to_params('settings.decay'))
        if neutralization is not None:
            params.append(f"settings.neutralization={neutralization}")
        if truncation is not None:
            params.append(truncation.to_params('settings.truncation'))
        if unit_handling is not None:
            params.append(f"settings.unitHandling={unit_handling}")
        if nan_handling is not None:
            params.append(f"settings.nanHandling={nan_handling}")
        if pasteurization is not None:
            params.append(f"settings.pasteurization={pasteurization}")
        if sharpe is not None:
            params.append(sharpe.to_params('os.sharpe'))
        if returns is not None:
            params.append(returns.to_params('os.returns'))
        if pnl is not None:
            params.append(pnl.to_params('is.pnl'))
        if turnover is not None:
            params.append(turnover.to_params('os.turnover'))
        if drawdown is not None:
            params.append(drawdown.to_params('os.drawdown'))
        if margin is not None:
            params.append(margin.to_params('os.margin'))
        if fitness is not None:
            params.append(fitness.to_params('os.fitness'))
        if book_size is not None:
            params.append(book_size.to_params('is.bookSize'))
        if long_count is not None:
            params.append(long_count.to_params('is.longCount'))
        if short_count is not None:
            params.append(short_count.to_params('is.shortCount'))
        if sharpe60 is not None:
            params.append(sharpe60.to_params('os.sharpe60'))
        if sharpe125 is not None:
            params.append(sharpe125.to_params('os.sharpe125'))
        if sharpe250 is not None:
            params.append(sharpe250.to_params('os.sharpe250'))
        if sharpe500 is not None:
            params.append(sharpe500.to_params('os.sharpe500'))
        if os_is_sharpe_ratio is not None:
            params.append(os_is_sharpe_ratio.to_params('os.osISSharpeRatio'))
        if pre_close_sharpe is not None:
            params.append(pre_close_sharpe.to_params('os.preCloseSharpe'))
        if pre_close_sharpe_ratio is not None:
            params.append(pre_close_sharpe_ratio.to_params('os.preCloseSharpeRatio'))
        if self_correlation is not None:
            params.append(self_correlation.to_params('is.selfCorrelation'))
        if prod_correlation is not None:
            params.append(prod_correlation.to_params('is.prodCorrelation'))
        if order is not None:
            params.append(f"order={order}")
        params.append(f"limit={limit}")
        params.append(f"offset={offset}")
        params.extend(others)
        return self.get(URL_USERS_SELF_ALPHAS + '?' + '&'.join(params), *args, **kwargs)

    def filter_alphas(
        self,
        *args,
        limit: int = 100,
        offset: int = 0,
        **kwargs,
    ) -> Generator[Response, None, None]:
        return (
            self.filter_alphas_limited(*args, limit=limit, offset=offset, **kwargs)
            for offset in range(
                offset,
                self.filter_alphas_limited(
                    *args, limit=1, offset=offset, **kwargs
                ).json()['count'],
                limit,
            )
        )

    def patch_properties(
        self,
        alpha_id: str,
        *args,
        **kwargs,
    ) -> Response:
        raise NotImplementedError()
        return self.patch(URL_ALPHAS_ALPHAID.format(alpha_id), *args, **kwargs)
