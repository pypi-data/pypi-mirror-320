from decimal import Decimal
from .constants import MAX_PROFIT_P, MAX_STOP_LOSS_P, PRECISION_2, PRECISION_6, PRECISION_12, PRECISION_18, LIQ_THRESHOLD_P

#
# This is a copy-cat of formulae repo originally written in TypeScript
#

#
# GetStopLossPrice and GetTakeProfitPrice are consolidated into one function.
# bool is_tp is True if we want to calculate the take profit price, False if we want to calculate the stop loss price
#


def GetTakeProfitPrice(is_tp: bool, open_price: Decimal, leverage: Decimal, long: bool, profit_p: Decimal) -> Decimal:
    """
    Calculate the take profit / stop loss price based on desired profit percentage (aka: MAX_PROFIT_P=900 or MAX_STOP_LOSS_P=85).

    Args:
        open_price (Decimal): The opening price of the trade
        profit_p (Decimal): The desired profit percentage
        leverage (Decimal): The leverage amount
        long (bool): Whether this is a long position
        profit_p (Decimal): The desired profit percentage - 900% for Tp or 85% for SL

    Returns:
        str: The Tp / SL price as a string
    """

    open_price = Decimal(open_price)
    profit_p = Decimal(profit_p)
    leverage = Decimal(leverage)

    price_diff = (open_price * profit_p) / (leverage * Decimal('100'))

    if (is_tp):
        price = open_price + price_diff if long else open_price - price_diff
    else:
        price = open_price - price_diff if long else open_price + price_diff

    return Decimal(price if price > 0 else '0')


def CurrentTradeProfitP(open_price: str, current_price: str, long: bool, leverage: str) -> str:
    """
    Calculate the current trade profit percentage.

    Args:
        open_price (str): The opening price of the trade
        current_price (str): The current price
        long (bool): Whether this is a long position
        leverage (str): The leverage amount

    Returns:
        str: The profit percentage as a string
    """
    try:

        open_price_d = Decimal(open_price)
        current_price_d = Decimal(current_price)
        leverage_d = Decimal(leverage)

        if long:
            price_diff = current_price_d - open_price_d
        else:
            price_diff = open_price_d - current_price_d

        profit_p = (price_diff / open_price_d) * (leverage_d)

        if profit_p > MAX_PROFIT_P:
            return (MAX_PROFIT_P)
        else:
            return (profit_p)
    except Exception as e:
        return str(e)


def GetTradeLiquidationPrice(
    open_price: str,
    long: bool,
    collateral: str,
    leverage: str,
    rollover_fee: str,
    funding_fee: str
) -> Decimal:
    try:
        open_price = Decimal(open_price)
        collateral = Decimal(collateral)
        rollover_fee = Decimal(rollover_fee)
        funding_fee = Decimal(funding_fee)
        leverage = Decimal(leverage)

        liq_price_distance = (
            open_price *
            (collateral * Decimal(LIQ_THRESHOLD_P) / Decimal(100) - rollover_fee - funding_fee) /
            collateral /
            leverage
        )

        # print('# liq_price_distance', liq_price_distance)
        liq_price = open_price - liq_price_distance if long else open_price + liq_price_distance

        liq_price = liq_price if liq_price > 0 else 0
        # print('---> liq_price', liq_price)
        return liq_price

    except Exception as error:
        raise Exception(f"Unable to compute Liquidation Price: {error}")


def GetCurrentRolloverFee(
    acc_rollover: str,
    last_rollover_block: str,
    rollover_fee_per_block: str,
    latest_block: str
) -> Decimal:
    try:
        acc_rollover = Decimal(acc_rollover)
        last_rollover_block = Decimal(last_rollover_block)
        rollover_fee_per_block = Decimal(rollover_fee_per_block)
        latest_block = Decimal(latest_block)
        current_fee = acc_rollover + \
            (latest_block - last_rollover_block) * rollover_fee_per_block
        return current_fee

    except Exception as error:
        raise Exception(f"Unable to compute Current Rollover Fee: {error}")


def GetTradeRolloverFee(
    trade_rollover: str,
    current_rollover: str,
    collateral: str,
    leverage: str
) -> Decimal:
    try:
        current_rollover = Decimal(current_rollover)
        trade_rollover = Decimal(trade_rollover)
        collateral = Decimal(collateral)
        leverage = Decimal(leverage)

        rollover_fee = (
            (current_rollover - trade_rollover) *
            collateral *
            leverage /
            PRECISION_18 /
            PRECISION_2
        )
        return rollover_fee

    except Exception as error:
        raise Exception(f"Unable to compute Trade Rollover Fee: {error}")


def GetTradeFundingFee(
    trade_funding: str,
    current_funding: str,
    collateral: str,
    leverage: str
) -> Decimal:
    try:
        current_funding = Decimal(current_funding)
        trade_funding = Decimal(trade_funding)
        collateral = Decimal(collateral)
        leverage = Decimal(leverage)

        funding_fee = (
            (current_funding - trade_funding) *
            collateral *
            leverage /
            PRECISION_18 /
            PRECISION_2
        )
        return funding_fee

    except Exception as error:
        raise Exception(f"Unable to compute Trade Funding Fee: {error}")


def GetFundingRate(
    acc_funding_long: str,
    acc_funding_short: str,
    last_funding_rate: str,
    last_funding_velocity: str,
    max_funding_fee_per_block: str,
    last_funding_block: str,
    latest_block: str,
    long_oi: str,
    short_oi: str
) -> dict:
    try:
        acc_funding_long = Decimal(acc_funding_long)
        acc_funding_short = Decimal(acc_funding_short)
        last_funding_rate = Decimal(last_funding_rate)
        last_funding_velocity = Decimal(last_funding_velocity)
        max_funding_fee_per_block = Decimal(max_funding_fee_per_block)
        last_funding_block = Decimal(last_funding_block)
        latest_block = Decimal(latest_block)
        long_oi = Decimal(long_oi)
        short_oi = Decimal(short_oi)

        block_diff = latest_block - last_funding_block

        # Calculate skew
        total_oi = long_oi + short_oi
        skew = Decimal('0')
        if total_oi > 0:
            skew = (long_oi - short_oi) / total_oi

        # Calculate funding rate
        funding_rate = last_funding_rate + last_funding_velocity * block_diff

        # Cap funding rate
        if funding_rate > max_funding_fee_per_block:
            funding_rate = max_funding_fee_per_block
        elif funding_rate < -max_funding_fee_per_block:
            funding_rate = -max_funding_fee_per_block

        # Calculate accumulated funding
        funding_long = acc_funding_long + funding_rate * block_diff
        funding_short = acc_funding_short - funding_rate * block_diff

        return {
            'accFundingLong': str(funding_long),
            'accFundingShort': str(funding_short),
            'skew': str(skew)
        }

    except Exception as error:
        raise Exception(f"Unable to compute Funding Rate: {error}")


def GetPriceImpact(
    mid_price: str,
    bid_price: str,
    ask_price: str,
    spread_p: str,
    is_limit: bool,
    is_buy: bool,
    is_close: bool,
    trade_size: str,
    trade_size_ref: str
) -> dict:
    try:
        mid_price = Decimal(mid_price)
        bid_price = Decimal(bid_price)
        ask_price = Decimal(ask_price)
        spread_p = Decimal(spread_p)
        trade_size = Decimal(trade_size)
        trade_size_ref = Decimal(trade_size_ref)

        # Calculate base spread
        base_spread = (ask_price - bid_price) / mid_price

        # Calculate impact spread
        impact_spread = base_spread * (trade_size / trade_size_ref)

        # Calculate price after impact
        price_after_impact = mid_price
        if not is_limit:
            if is_buy:
                price_after_impact = mid_price * \
                    (Decimal('1') + impact_spread / Decimal('2'))
            else:
                price_after_impact = mid_price * \
                    (Decimal('1') - impact_spread / Decimal('2'))

        return {
            'priceAfterImpact': str(price_after_impact),
            'impactSpread': str(impact_spread)
        }

    except Exception as error:
        raise Exception(f"Unable to compute Price Impact: {error}")


def CurrentTradeProfitRaw(
    open_price: str,
    current_price: str,
    is_buy: bool,
    leverage: str,
    collateral: str
) -> str:
    try:
        open_price = Decimal(open_price)
        current_price = Decimal(current_price)
        leverage = Decimal(leverage)
        collateral = Decimal(collateral)

        # Calculate price difference based on position direction
        if is_buy:
            price_diff = current_price - open_price
        else:
            price_diff = open_price - current_price

        # Calculate profit
        profit = (price_diff * collateral * leverage) / \
            (open_price * PRECISION_2)

        return str(profit)

    except Exception as error:
        raise Exception(f"Unable to compute Current Trade Profit Raw: {error}")


def CurrentTotalProfitRaw(
    open_price: str,
    current_price: str,
    is_buy: bool,
    leverage: str,
    collateral: str,
    rollover_fee: str,
    funding_fee: str
) -> str:
    try:
        # Get trade profit
        trade_profit = Decimal(CurrentTradeProfitRaw(
            open_price,
            current_price,
            is_buy,
            leverage,
            collateral
        ))

        # Subtract fees
        total_profit = trade_profit - \
            Decimal(rollover_fee) - Decimal(funding_fee)

        return str(total_profit)

    except Exception as error:
        raise Exception(f"Unable to compute Current Total Profit Raw: {error}")


def CurrentTotalProfitP(total_profit: str, collateral: str) -> str:
    try:
        total_profit = Decimal(total_profit)
        collateral = Decimal(collateral)

        # Calculate profit percentage
        profit_percentage = (total_profit * PRECISION_6) / collateral

        # Cap at MAX_PROFIT_P if needed
        if profit_percentage > MAX_PROFIT_P:
            return str(MAX_PROFIT_P)

        return str(profit_percentage)

    except Exception as error:
        raise Exception(
            f"Unable to compute Current Total Profit Percentage: {error}")

# given desired TP percentage, like 35, 50, 75, 100, 500 and 900 which is max: gives you the TP price
