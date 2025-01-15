from datetime import datetime
from decimal import Decimal
import os
from humanize import naturaltime
from web3 import Web3
from ast import literal_eval

from .constants import MAX_PROFIT_P, MAX_STOP_LOSS_P
from .formulae import GetTakeProfitPrice


def send_slack_message(client, from_username, message):
    # Send a message
    if client is not None:
        message = f'{from_username}: {message}'
        client.chat_postMessage(
            channel="telegram-bot",
            text=message,
            username="User Feedback"
        )
    else:
        print(
            f'********* client is None, from_username: {from_username}, message: {message}')


def get_asset_group_name(from_asset, to_asset):
    if from_asset in ['BTC', 'ETH', 'SOL']:
        return 'crypto'
    elif from_asset in ['HG', 'CL', 'XAU', 'XAG', 'XPD', 'XPT', 'NG', 'LCO']:
        return 'commodities'
    elif from_asset in ['SPX', 'HSI', 'NIK', 'FTS', 'DAX']:
        return 'indices'
    elif from_asset in ['EUR', 'GBP'] or (from_asset == 'USD' and to_asset == 'JPY'):
        return 'forex'
    else:
        print('------> get_asset_group_name need to map asset asset_group_name',
              from_asset, to_asset)
        return ''

#
# rename market_price as open_price. Pass Leverage.
# Get the None value here returned by calling GetTakeProfitPrice
# and consolidate the logic of these 2 functions to one
#


def get_asset_change_emoji(asset_group_name, change, period_hours):
    """
    Returns an emoji indicating price movement severity based on asset type and time period.
    Different assets have different volatility profiles:
    - Crypto: More volatile but realistic (2% in 24h is notable, 100% in 1y is extreme)
    - Commodities: Medium volatility
    - Forex/Indices: Lower volatility (tighter thresholds)
    """
    # Define thresholds for each period and asset group (values in percentages)
    thresholds = {
        'crypto': {
            1: [0.3, 0.7, 1.2, 2, 3],      # 1h
            8: [0.7, 1.5, 2.5, 4, 6],      # 8h
            24: [1, 2, 4, 6, 8],           # 24h
            365*24: [10, 25, 50, 75, 100]  # 1y: More realistic yearly moves
        },
        'commodities': {
            1: [0.2, 0.5, 1, 2, 3],        # 1h
            8: [0.5, 1, 2, 3, 5],          # 8h
            24: [1, 2, 3, 5, 7],           # 24h
            365*24: [10, 20, 30, 50, 70]   # 1y
        },
        'forex': {
            1: [0.1, 0.2, 0.3, 0.5, 1],    # 1h
            8: [0.2, 0.4, 0.6, 1, 1.5],    # 8h
            24: [0.3, 0.6, 1, 1.5, 2],     # 24h
            365*24: [5, 10, 15, 20, 25]    # 1y
        },
        'indices': {
            1: [0.2, 0.4, 0.6, 1, 1.5],    # 1h
            8: [0.4, 0.8, 1.2, 2, 3],      # 8h
            24: [0.8, 1.5, 2.5, 3.5, 5],   # 24h
            365*24: [8, 15, 25, 35, 45]    # 1y
        }
    }

    if period_hours not in thresholds[asset_group_name]:
        return ''

    # Get absolute change for comparison
    abs_change = abs(change)
    period_thresholds = thresholds[asset_group_name][period_hours]

    # Determine severity level
    if abs_change < period_thresholds[0]:
        emoji = ''  # Minimal change
    elif abs_change < period_thresholds[1]:
        emoji = '📈' if change > 0 else '📉'
    elif abs_change < period_thresholds[2]:
        emoji = '⬆️' if change > 0 else '⬇️'
    elif abs_change < period_thresholds[3]:
        emoji = '🔥' if change > 0 else '💧'
    elif abs_change < period_thresholds[4]:
        emoji = '🚀' if change > 0 else '🌪'
    else:
        emoji = '⚡️' if change > 0 else '💀'

    return f' {emoji}'


def get_tp_sl_min_max_allowed_values(is_long: bool, market_price: Decimal, leverage: Decimal, is_tp: bool) -> tuple[Decimal, Decimal]:
    """
    Returns (min_allowed, max_allowed) tuple for take profit or stop loss prices based on position direction

    Args:
        is_long: True if long position, False if short
        market_price: Current market price
        is_tp: True if checking take profit, False if checking stop loss
    """

    tp_or_sl_price = GetTakeProfitPrice(
        is_tp, market_price, leverage, is_long, MAX_PROFIT_P if is_tp else MAX_STOP_LOSS_P)
    if is_tp:
        # Take profit must be above market for longs, below for shorts
        return (
            (Decimal(market_price), tp_or_sl_price) if is_long else
            (tp_or_sl_price, Decimal(market_price))
        )
    else:
        # Stop loss must be below market for longs, above for shorts
        return (
            (tp_or_sl_price, Decimal(market_price)) if is_long else
            (Decimal(market_price), tp_or_sl_price)
        )


def is_valid_evm_address(address):
    is_valid = Web3.is_address(address)
    print('----->is_valid_evm_address called with',
          address, 'and returns', is_valid)
    return is_valid

# returns (is_valid, percentage_inputted or None is not relevant, not relevant is is_valid is False)


def is_valid_input(text, validation):

    if validation is None:
        return True, None

    if 'is_address_and_none_self' in validation and validation['is_address_and_none_self']:
        trader_address = validation['own_address']
        return is_valid_evm_address(text) and (text).lower() != trader_address.lower(), None

    # Check if it's a valid decimal number
    if not is_valid_decimal(text):
        if 'percentage_allowed_for' not in validation:
            return False, None
        else:
            # replace only 1 occurrence of '%' so 5%% isn't valid
            text = text.replace('%', '', 1)
            if not is_valid_decimal(text) or Decimal(text) == 0:  # cant accept 0%
                return False, None
            else:
                return True, Decimal(text)

    # By now, text is not specified as a percentage

    # Convert to Decimal for comparison
    value = Decimal(text)

    # Special case: if zero_to_remove is present and value is 0
    if 'zero_to_remove' in validation and validation['zero_to_remove'] and value == 0:
        return True, False

    if ('zero_to_remove' not in validation or not validation['zero_to_remove']) and value == 0:
        return False, False

    # Check minimum value if specified
    if 'min' in validation and value < Decimal(validation['min']):
        return False, False

    # Check maximum value if specified
    if 'max' in validation and value > Decimal(validation['max']):
        return False, False

    return True, False


def get_period_hours_text(period_hours):
    if period_hours == 1:
        return '1h'
    elif period_hours == 8:
        return '8h'
    elif period_hours == 24:
        return '24h'
    elif period_hours == 365*24:
        return '1y'


def build_asset_callback_data(asset_id, period_hours=None):
    return f'chooseAsset|{asset_id}|{period_hours if period_hours else "24"}'

# period_hours is 1, 8, 24, 8760 (365*24)


def parse_performances(performances, period_hours):
    try:
        if performances:
            if period_hours == 24:
                low = Decimal(performances['low24h'])
                high = Decimal(performances['high24h'])
                change = Decimal(performances['24hChange'])
            elif period_hours == 8:
                low = Decimal(performances['low8h'])
                high = Decimal(performances['high8h'])
                change = Decimal(performances['8hChange'])
            elif period_hours == 1:
                low = Decimal(performances['low1h'])
                high = Decimal(performances['high1h'])
                change = Decimal(performances['1hChange'])
            elif period_hours == 365*24:
                low = Decimal(performances['low1y']
                              ) if 'low1y' in performances else None
                high = Decimal(performances['high1y']
                               ) if 'high1y' in performances else None
                change = Decimal(
                    performances['1yChange']) if '1yChange' in performances else None
            else:
                low = None
                high = None
                change = None

            return low, high, change
        else:
            return Decimal(0), Decimal(0), Decimal(0)

    except Exception as e:
        return Decimal(0), Decimal(0), Decimal(0)


def get_tp_sl_prices(trade_params):
    tp_price = 0
    sl_price = 0

    if 'tp' in trade_params and str(trade_params['tp']) != '0':
        tp_price = float(trade_params['tp'])

    if 'sl' in trade_params and str(trade_params['sl']) != '0':
        sl_price = float(trade_params['sl'])

    return tp_price, sl_price


def get_oi_usage_emoji(oi, max_oi_cap):
    oi_percent = oi/max_oi_cap*100
    if oi_percent >= 100:
        return '🚫'
    elif oi_percent > 80:
        return '🔥🔥🔥'
    elif oi_percent > 50:
        return '🔥🔥'
    elif oi_percent > 40:
        return '🔥'
    else:
        return ''


def get_validation_text(validation_dict):
    if 'min' in validation_dict and 'max' in validation_dict:
        return f"between {validation_dict['min']} and {validation_dict['max']}"
    else:
        if 'min' in validation_dict and 'max' not in validation_dict:
            return f"equal or above {validation_dict['min']}"
        elif 'max' in validation_dict and 'min' not in validation_dict:
            return f"equal or below {validation_dict['max']}"
        else:
            return ''


def format_awaiting_input_text(text, validation_dict, market_mid_price=None):
    if 'min' in validation_dict and 'max' in validation_dict:
        from_to_str = f"range:\n{validation_dict['min']} - {validation_dict['max']}"
    else:
        if 'min' in validation_dict and 'max' not in validation_dict:
            from_to_str = f"min. {validation_dict['min']}"
        elif 'max' in validation_dict and 'min' not in validation_dict:
            from_to_str = f"max. {validation_dict['max']}"
        else:
            from_to_str = ''

    note = f"\nOr 0 to remove" if 'zero_to_remove' in validation_dict and validation_dict[
        'zero_to_remove'] else ''

    tp_sl_examples = ""
    if 'percentage_allowed_for' in validation_dict:
        purpose = validation_dict['percentage_allowed_for']
        percentages = [25, 50, 75, 100, 500,
                       900] if purpose == "tp" else [5, 10, 25, 50, 85]

        tp_sl_examples = f"\n\nOr specify {purpose.title()} as a percentage, i.e:\n"
        for percent in percentages:
            price = GetTakeProfitPrice(
                is_tp=(purpose == "tp"),
                open_price=validation_dict['metadata']['open_price'],
                leverage=validation_dict['metadata']['leverage'],
                long=validation_dict['metadata']['is_long'],
                profit_p=percent
            )
            tp_sl_examples += f"{percent}% 👉 ${format_with_precision(price, precision=5)}\n"

    return f'{text}\n\n{from_to_str}{tp_sl_examples}{note}'


def get_profit_emoji(profit_percent):
    if profit_percent >= 80:
        return '💰💰'
    elif profit_percent >= 60:
        return '💰'
    elif profit_percent >= 50:
        return '🚀'
    elif profit_percent >= 20:
        return '🔥'
    elif profit_percent > -3:
        return ''
    elif profit_percent >= -5:
        return '🤨'
    elif profit_percent >= -20:
        return '😟'
    elif profit_percent >= -25:
        return '😲'
    elif profit_percent >= -30:
        return '😢'
    elif profit_percent >= -40:
        return '😱'
    elif profit_percent >= -50:
        return '💣'
    else:
        return '💀'  # Skull for severe losses


def get_oi_in_usd(oi, price):
    return format_with_precision(Web3.from_wei(int(oi) * price, 'ether'), precision=2)


def get_oi_state(pair_details, mid_price):
    long_oi = get_oi_in_usd(pair_details['longOI'], mid_price)
    short_oi = get_oi_in_usd(pair_details['shortOI'], mid_price)

    max_oi_cap = format_with_precision(Web3.from_wei(
        int(pair_details['maxOI']), 'mwei'), precision=2)

    return Decimal(long_oi), Decimal(short_oi), Decimal(max_oi_cap)


def format_with_precision(number, precision):
    """
    Formats a number to a specified decimal precision, removing trailing zeros.

    Args:
        number: The number to be formatted (can be int, float, or numeric string)
        precision (int): Maximum number of decimal places to round to

    Returns:
        str: Formatted number with up to specified decimal precision, trailing zeros removed
    """
    try:
        if callable(number):
            raise TypeError("Input cannot be a function")

        float_number = float(number)
        precision = int(precision)

        # Format with specified precision first
        formatted = "{:.{}f}".format(round(float_number, precision), precision)
        # Remove trailing zeros after decimal point, but keep at least one digit before decimal
        formatted = formatted.rstrip('0').rstrip(
            '.') if '.' in formatted else formatted

        return float(formatted)

    except (TypeError, ValueError) as e:
        raise TypeError(f"Invalid input: {e}")

# my_time is datetime.fromtimestamp


def format_time_ago(my_time):
    ago = naturaltime(datetime.now() - my_time).replace('minutes',
                                                        'm').replace('seconds', 's').replace('hours', 'h').replace('days', 'd')
    return f'{my_time.strftime("%H:%M %a %b %-d")} ({ago})'


def get_order_details(order_details):
    open_price = Web3.from_wei(int(order_details['openPrice']), 'ether')

    limit_order_created_time = datetime.fromtimestamp(
        int(order_details['initiatedAt']))

    leverage = Web3.from_wei(int(order_details['leverage']), 'kwei')*10
    collateral = Web3.from_wei(int(order_details['collateral']), 'mwei')
    is_long = order_details['isBuy']
    limit_type = order_details['limitType']
    pairIndex, index = parse_limit_order_id(order_details['id'])

    sl_price = Web3.from_wei(int(order_details['stopLossPrice']), 'ether')
    tp_price = Web3.from_wei(int(order_details['takeProfitPrice']), 'ether')

    atLeastTradeNotional = 0
    if open_price:
        atLeastTradeNotional = collateral*leverage/open_price

    return limit_type, sl_price, tp_price, open_price, leverage, limit_order_created_time, collateral, pairIndex, index, is_long, atLeastTradeNotional


def get_trade_details(trade_details):
    # print('\n\nget_trade_details called with trade_details\n\n', trade_details, '\n\n')
    open_price = Web3.from_wei(int(trade_details['openPrice']), 'ether')
    sl_price = Web3.from_wei(int(trade_details['stopLossPrice']), 'ether')
    tp_price = Web3.from_wei(int(trade_details['takeProfitPrice']), 'ether')
    tradeNotional = Web3.from_wei(int(trade_details['tradeNotional']), 'ether')
    trans_time = datetime.fromtimestamp(int(trade_details['timestamp']))
    leverage = Web3.from_wei(int(trade_details['leverage']), 'kwei')*10
    collateral = Web3.from_wei(int(trade_details['collateral']), 'mwei')
    is_long = trade_details['isBuy']
    pairIndex = trade_details['pair']['id']
    index = trade_details['index']

    return open_price, round(tradeNotional, 18), trans_time, leverage, collateral, pairIndex, index, is_long, sl_price, tp_price


def parse_limit_order_id(limit_order_id):
    # 0x3750a14869d419f1069cbf7cbe47a89b2dc1d4c4_0_0
    trader, pairIndex, index = limit_order_id.split('_')

    return pairIndex, index


def is_numeric(value):
    try:
        float(value)
        return True
    except ValueError:
        return False


def fromErrorCodeToMessage(error_code):
    # ----->fromErrorCodeToMessage(error_code) called with ('execution reverted: ERC20: transfer amount exceeds balance', '0x08c379a00000000000000000000000000000000000000000000000000000000000000020000000000000000000000000000000000000000000000000000000000000002645524332303a207472616e7366657220616d6f756e7420657863656564732062616c616e63650000000000000000000000000000000000000000000000000000')
    # ----->Did't find the error, so returning - fromErrorCodeToMessage(error_code) returns Unknown error (missing in error_map?)

    print('----->fromErrorCodeToMessage(error_code) called with', str(error_code))

    # Create reverse mapping of hash -> error name
    error_map = {
        "80a71fc5": "AboveMaxAllowedCollateral()",
        "f77a8069": "AlreadyMarketClosed(address,uint16,uint8)",
        "eca695e1": "BelowMinLevPos()",
        "5be5878a": "DelegatedActionFailed()",
        "46c4ede2": "ExposureLimits()",
        "4f285592": "IsContract(address)",
        "084986e7": "IsDone()",
        "1309a563": "IsPaused()",
        "5c12ea62": "MaxPendingMarketOrdersReached(address)",
        "e6f47fab": "MaxTradesPerPairReached(address,uint16)",
        "2a917859": "NoDelegate(address)",
        "a35ee470": "NoLimitFound(address,uint16,uint8)",
        "17e08e97": "NoTradeFound(address,uint16,uint8)",
        "efa9e5be": "NoTradeToTimeoutFound(uint256)",
        "c7fe4d00": "NotCloseMarketTimeoutOrder(uint256)",
        "502b946d": "NotDelegate(address,address)",
        "093650d5": "NotGov(address)",
        "1add0915": "NotOpenMarketTimeoutOrder(uint256)",
        "432b6c83": "NotTradesUpKeep(address)",
        "df17e316": "NotWhitelisted(address)",
        "5ac89f62": "NotYourOrder(uint256,address)",
        "f3d0b126": "NullAddr()",
        "cb87b762": "PairNotListed(uint16)",
        "dd9397bb": "TriggerPending(address,uint16,uint8)",
        "3e0b1869": "WaitTimeout(uint256)",
        "35fe85c5": "WrongLeverage(uint32)",
        "5863f789": "WrongParams()",
        "083fbd78": "WrongSL()",
        "a41bb918": "WrongTP()"
    }

    # Search for any of the known error hashes within the error_code string
    for hash_code, error_message in error_map.items():
        if hash_code in str(error_code):
            ret = error_message
            print('----->fromErrorCodeToMessage(error_code) returns', ret)
            return str(ret), None

    # If we couldn't find the error in error_map, try to parse the error
    try:
        # Convert string representation to dictionary if needed
        error_dict = error_code if isinstance(
            error_code, dict) else literal_eval(str(error_code))
        if isinstance(error_dict, dict) and 'message' in error_dict:
            if 'insufficient funds for gas * price + value' in error_dict['message']:
                suggestion = 'Please top up your account with more ETH'
                return error_dict["message"], suggestion
            else:
                return error_dict['message'], None
    except (ValueError, SyntaxError):
        pass

    if 'execution reverted: ERC20: transfer amount exceeds balance' in str(error_code):
        suggestion = 'Please top up your account with more USDC'
        return 'execution reverted: ERC20: transfer amount exceeds balance', suggestion

    ret = 'Unknown error (missing in error_map?)'
    print('----->Did\'t find the error, so returning - fromErrorCodeToMessage(error_code) returns', ret)
    return str(ret), None


# def is_production():
#     return 'sepolia' not in (os.getenv('RPC_PROVIDER')).lower()


def get_arbiscan_transaction_url(transaction_hash):
    if (is_production()):
        return f'https://arbiscan.io/tx/0x{transaction_hash}'
    else:
        return f'https://sepolia.arbiscan.io/tx/0x{transaction_hash}'


def get_max_leverage_and_min_leverage_position(pair_details):
    max_leverage = int(pair_details['maxLeverage']) / 100
    min_leverage_position = int(pair_details['fee']['minLevPos']) / 10 ** 6

    if (max_leverage == 0):
        max_leverage = int(pair_details['group']['maxLeverage']) / 100

    return int(max_leverage), int(min_leverage_position)


def to_base_units(amount: float, decimals: int = 6) -> int:
    """
    Converts a decimal number to base units by multiplying by 10^decimals

    Args:
        amount (float): The amount to convert (e.g., 1.23)
        decimals (int, optional): Number of decimal places. Defaults to 6 for USDC.

    Returns:
        int: The amount in base units (e.g., 1.23 -> 1230000 for decimals=6)
    """
    return int(float(amount) * 10**decimals)


def convert_to_scaled_integer(value, precision=5, scale=18):
    # First scale to the precision we want to preserve (e.g., 5 decimal places)
    precise_value = round(Decimal(value) * (10 ** precision))
    # Then pad with zeros to reach 18 decimals
    scaled_value = precise_value * (10 ** (scale - precision))
    return scaled_value


def is_valid_decimal(s, must_be_positive=True):
    try:
        float(s)
    except ValueError:
        return False
    else:
        if must_be_positive and float(s) < 0:
            return False
        return True


def format_available_balance(balance_of_ether, usdc_balance):
    eth_warning = ' ✖️ <i>gas</i>' if Decimal(
        balance_of_ether) < Decimal('0.00015') else ''
    return f'Available: {format_with_precision(usdc_balance, precision=2)} USDC, {format_with_precision(balance_of_ether, precision=5)} ETH{eth_warning}'


def format_current_portfolio(total_open_trades_net_value, usdc_balance):
    return f'Wallet worth: <b>{format_with_precision(Decimal(total_open_trades_net_value) + Decimal(usdc_balance), precision=2)} USDC</b>'


def get_asset_name(from_asset, to_asset):
    asset = f'{from_asset}/{to_asset}'
    switch = {
        'BTC/USD': 'Bitcoin',
        'ETH/USD': 'Ethereum',
        'SOL/USD': 'Solana',
        'XAU/USD': 'Gold',
        'XAG/USD': 'Silver',
        'EUR/USD': 'Euro',
        'GBP/USD': 'Pound',
        'USD/JPY': 'Yen',
        'CL/USD': 'Crude Oil',
        'NG/USD': 'Natural Gas',
        'HG/USD': 'Copper',
        'SPX/USD': 'S&P 500',
    }
    return switch.get(asset, asset)


def convert_decimals(obj):
    if isinstance(obj, dict):
        return {key: convert_decimals(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_decimals(item) for item in obj]
    elif isinstance(obj, Decimal):
        return str(obj)  # or float(obj) if you prefer
    return obj

# timestamp is a string in seconds as returned from graph
