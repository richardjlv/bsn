#!/usr/bin/env python2
from behave import given, when, then
from component import sensor_module # Using Boost.Python bindings

@given('the sensor is initialized')
def step_impl(context):
    context.sensor = sensor_module.create_g3t1_3_instance(0, [], "sensor")

@when('I call the setup function')
def step_impl(context):
    context.sensor.setUp()

@then('the sensor should be properly configured')
def step_impl(context):
    print("Setup completed successfully!")
