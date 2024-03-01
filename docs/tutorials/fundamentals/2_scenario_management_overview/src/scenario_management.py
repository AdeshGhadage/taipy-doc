from taipy import Config
import taipy as tp
import pandas as pd
import datetime as dt


data = pd.read_csv("https://raw.githubusercontent.com/Avaiga/taipy-getting-started-core/develop/src/daily-min-temperatures.csv")


# Normal function used by Taipy
def predict(historical_temperature: pd.DataFrame, date_to_forecast: dt.datetime) -> float:
    print(f"Running baseline...")
    historical_temperature["Date"] = pd.to_datetime(historical_temperature["Date"])
    historical_same_day = historical_temperature.loc[
        (historical_temperature["Date"].dt.day == date_to_forecast.day) &
        (historical_temperature["Date"].dt.month == date_to_forecast.month)
    ]
    return historical_same_day["Temp"].mean()

# Configuration of Data Nodes
historical_temperature_cfg = Config.configure_data_node("historical_temperature")
date_to_forecast_cfg = Config.configure_data_node("date_to_forecast")
predictions_cfg = Config.configure_data_node("predictions")

# Configuration of tasks
task_predict_cfg = Config.configure_task("predict",
                                        predict,
                                        [historical_temperature_cfg, date_to_forecast_cfg],
                                        predictions_cfg)

# Configuration of scenario
scenario_cfg = Config.configure_scenario(id="my_scenario", 
                                         task_configs=[task_predict_cfg])

Config.export("config.toml")

if __name__ == "__main__":
    # Run of the Core
    tp.Core().run()

    # Creation of the scenario and execution
    scenario = tp.create_scenario(scenario_cfg)
    scenario.historical_temperature.write(data)
    scenario.date_to_forecast.write(dt.datetime.now())
    tp.submit(scenario)

    print("Value at the end of task", scenario.predictions.read())

    def save(state):
        state.scenario.historical_temperature.write(data)
        state.scenario.date_to_forecast.write(state.date)
        state.refresh("scenario")
        tp.gui.notify(state, "s", "Saved! Ready to submit")

    date = None
    scenario_md = """
<|{scenario}|scenario_selector|>

Select a Date
<|{date}|date|on_change=save|active={scenario}|>

Run the scenario
<|{scenario}|scenario|>
<|{scenario}|scenario_dag|>

View all the information on your prediction here
<|{scenario.predictions}|data_node|>
"""

    tp.Gui(scenario_md).run()
    