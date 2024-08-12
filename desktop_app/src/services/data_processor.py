import matplotlib.pyplot as plt
import pandas as pd

from desktop_app.src.utils import setup_logger

logger = setup_logger("data_processor")


class DataProcessor:
    @staticmethod
    def process_inventory_data(data):
        df = pd.DataFrame(data)
        total_value = (df['quantity'] * df['price']).sum()
        low_stock_items = df[df['quantity'] < df['reorder_point']]

        return {
            'total_items': len(df),
            'total_value': total_value,
            'low_stock_items': low_stock_items.to_dict('records')
        }

    @staticmethod
    def generate_sales_report(data):
        df = pd.DataFrame(data)
        df['date'] = pd.to_datetime(df['date'])
        daily_sales = df.groupby('date')['total'].sum().reset_index()

        plt.figure(figsize=(12, 6))
        plt.plot(daily_sales['date'], daily_sales['total'])
        plt.title('Daily Sales')
        plt.xlabel('Date')
        plt.ylabel('Total Sales')
        plt.savefig('sales_report.png')
        plt.close()

        return {
            'total_sales': df['total'].sum(),
            'average_order_value': df['total'].mean(),
            'best_selling_product': df.groupby('product_id')['quantity'].sum().idxmax()
        }

    @staticmethod
    def analyze_warehouse_efficiency(picking_data, shipping_data):
        picking_df = pd.DataFrame(picking_data)
        shipping_df = pd.DataFrame(shipping_data)

        avg_picking_time = picking_df['duration'].mean()
        avg_shipping_time = shipping_df['duration'].mean()

        efficiency_score = 100 - (avg_picking_time + avg_shipping_time) / 2

        return {
            'average_picking_time': avg_picking_time,
            'average_shipping_time': avg_shipping_time,
            'efficiency_score': efficiency_score
        }

    @staticmethod
    def forecast_demand(historical_data, periods=30):
        df = pd.DataFrame(historical_data)
        df['date'] = pd.to_datetime(df['date'])
        df = df.set_index('date')
        df = df.resample('D').sum()

        model = pd.DataFrame(df['quantity']).rolling(window=7).mean()
        forecast = model.shift(periods=1)

        plt.figure(figsize=(12, 6))
        plt.plot(df.index, df['quantity'], label='Actual')
        plt.plot(forecast.index, forecast['quantity'], label='Forecast')
        plt.title('Demand Forecast')
        plt.xlabel('Date')
        plt.ylabel('Quantity')
        plt.legend()
        plt.savefig('demand_forecast.png')
        plt.close()

        return forecast.tail(periods).to_dict()
