from taipy.core.notification import CoreEventConsumerBase, Event, Notifier
from time import sleep

def double(nb):
    return nb * 2

# Define a custom event consumer.
class MyEventConsumer(CoreEventConsumerBase):
    def process_event(self, event: Event):
        # Custom event processing logic here
        print(f"Received event created at : {event.creation_date}")

if __name__ == "__main__":
    import taipy as tp
    from taipy import Config

    print(f'(1) Number of jobs: {len(tp.get_jobs())}.')

    # Create a scenario configuration with 2 sequential tasks.
    input_data_node_cfg = Config.configure_data_node("my_input", default_data="My default data in my_input datanode.")
    print_task_cfg = Config.configure_task("print_task", print, input_data_node_cfg)
    scenario_config = Config.configure_scenario("my_scenario", [print_task_cfg])

    # Run the core service.
    tp.Core().run()
    
    # Register to the Notifier to retrieve a registration id and a registered queue.
    registration_id, registered_queue = Notifier.register()

    # Create a consumer and start it.
    consumer = MyEventConsumer(registration_id, registered_queue)
    consumer.start()

    # Create a scenario and submit it.
    scenario = tp.create_scenario(scenario_config)
    submission = tp.submit(scenario)

    sleep(1)

    # Stop the consumer and unregister from the Notifier.
    consumer.stop()
    Notifier.unregister(registration_id)
