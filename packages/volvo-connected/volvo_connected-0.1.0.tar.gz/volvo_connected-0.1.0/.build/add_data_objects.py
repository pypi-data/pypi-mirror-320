import json

def add_extra_schemas(data: any) -> any:
    # Adding RInstanceNumberWithUnit object
    # data["components"]["schemas"]["ResourceInstanceInt"] = {
    #     "type": "object",
    #     "properties": {
    #         "timestamp": {
    #             "type": "string",
    #             "format": "date-time"
    #         },
    #         "value": {
    #             "type": "number",
    #             "format": "int32"
    #         },
    #         "unit": {
    #             "type": "string"
    #         }
    #     }
    # }

    return data

def add_extra_properties_to_statistics(data: any) -> any:
    # Additional properties to the StatisticVals object
    for key in ['averageEnergyConsumption', 'tripMeterManual', 'tripMeterAutomatic']:
        data["components"]["schemas"]["StatisticVals"]["properties"][key] = {
            "$ref": "#/components/schemas/ResourceInstanceFloat"
        }
    
    # Changing type of the properties to RInstanceNumberWithUnit
    for key in ['averageSpeed', 'averageSpeedAutomatic', 'distanceToEmptyBattery']:
        data["components"]["schemas"]["StatisticVals"]["properties"][key] = {
            "$ref": "#/components/schemas/ResourceInstanceInteger"
        }

    return data

def add_extra_properties_to_fuel(data:any) -> any:
    for key in ['batteryChargeLevel']:
        data["components"]["schemas"]["FuelAmount"]["properties"][key] = {
            "$ref": "#/components/schemas/ResourceInstanceFloat"
        }
    return data


def transform_openapi_specs_objects_to_data(data: any, keys: list[str]) -> any:
   
    for key in keys:
        current_object = data["components"]["schemas"][key]
        if current_object is not None:
            new_object = {
                "type": "object",
                "properties": {
                    "data": current_object
                }
            }
            data["components"]["schemas"][key] = new_object
    
    return data

def transform_openapi_specs_objects_to_data_array(data: any, keys: list[str]) -> any:
    for key in keys:
        current_object = data["components"]["schemas"][key]
        if current_object is not None:
            new_object = {
                "type": "object",
                "properties": {
                    "data": {
                        "type": "array",
                        "items": current_object
                    }
                }
            }
            data["components"]["schemas"][key] = new_object
    
    return data

def transform_openapi_to_actual_api(file_path: str) -> None:
    with open(f'/workspaces/volvo_connected/.build/{file_path}', "r") as file:
        data = json.load(file)

    data = add_extra_schemas(data)
    data = add_extra_properties_to_statistics(data)
    data = add_extra_properties_to_fuel(data)

    data = transform_openapi_specs_objects_to_data_array(data, ["VehicleVin"])
    data = transform_openapi_specs_objects_to_data(data, [
        "Windows", 
        "Doors", 
        "EngineStatus", 
        "VehicleDetails", 
        "ExteriorWarning", 
        "OdometerValue",
        "FuelAmount", 
        "EngineDiagnostics",
        "Diagnostics", 
        "BrakeStatus",
        "CommandAccessibility",
        "Invoke",
        "InvokeUnlock"
      ])

    with open(f'/workspaces/volvo_connected/.build/volvo_connected_specs.json', "w") as file:
        json.dump(data, file, indent=2)

transform_openapi_to_actual_api("connected-vehicle-c3-specification_original.json")