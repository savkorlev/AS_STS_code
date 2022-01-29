
class Vehicle:
    def __init__(self, type: str, city: str, plateNr: str, fixed_cost_bool: bool):
        self.plateNr = plateNr
        self.type = type
        self.city = city
        self.max_duration = 600.0  # todo: get correct max durations for every city

        if city == "Paris":
            # city_tax = 0.10  # low end
            city_tax = 0.25  # I took the average from the expected toll range
            # city_tax = 0.40  # top end
        elif city == "NewYork":
            city_tax = 0.25
        elif city == "Shanghai":
            city_tax = 0.125

        if type == "MercedesBenzAtego":
            self.payload_kg = 2800
            self.payload_vol = 34.80 * 1000  # needs to be * 1000 because the volumes in nodes is given with unit m^3 * 10^-3
            self.range_km = 99999  # range for ICEVs is unlimited
            self.fixed_cost = 47.71 * fixed_cost_bool
            if city == "Paris":
                self.cost_km = 0.281
                self.cost_km_in = self.cost_km + city_tax  # only add city tax if vehicle is combustion
                self.cost_m = 0.383
            elif city == "NewYork":
                self.cost_km = 0.156
                self.cost_km_in = self.cost_km + city_tax
                self.cost_m = 0.429
            elif city == "Shanghai":
                self.cost_km = 0.178
                self.cost_km_in = self.cost_km + city_tax
                self.cost_m = 0.128

        elif type == "VWTransporter":
            self.payload_kg = 883
            self.payload_vol = 5.8 * 1000  # needs to be * 1000 because the volumes in nodes is given with unit m^3 * 10^-3
            self.range_km = 99999  # range for ICEVs is unlimited
            self.fixed_cost = 27.82 * fixed_cost_bool
            if city == "Paris":
                self.cost_km = 0.160
                self.cost_km_in = self.cost_km + city_tax
                self.cost_m = 0.369
            elif city == "NewYork":
                self.cost_km = 0.103
                self.cost_km_in = self.cost_km + city_tax
                self.cost_m = 0.459
            elif city == "Shanghai":
                self.cost_km = 0.113
                self.cost_km_in = self.cost_km + city_tax
                self.cost_m = 0.112

        elif type == "VWCaddy":
            self.payload_kg = 670
            self.payload_vol = 3.2 * 1000  # needs to be * 1000 because the volumes in nodes is given with unit m^3 * 10^-3
            self.range_km = 99999  # range for ICEVs is unlimited
            self.fixed_cost = 19.68 * fixed_cost_bool
            if city == "Paris":
                self.cost_km = 0.134
                self.cost_km_in = self.cost_km + city_tax
                self.cost_m = 0.369
            elif city == "NewYork":
                self.cost_km = 0.092
                self.cost_km_in = self.cost_km + city_tax
                self.cost_m = 0.459
            elif city == "Shanghai":
                self.cost_km = 0.099
                self.cost_km_in = self.cost_km + city_tax
                self.cost_m = 0.112

        elif type == "DeFuso":
            self.payload_kg = 2800
            self.payload_vol = 21.56 * 1000  # needs to be * 1000 because the volumes in nodes is given with unit m^3 * 10^-3
            self.range_km = 80  # range for BEV is limited
            self.fixed_cost = 48.21 * fixed_cost_bool
            if city == "Paris":
                self.cost_km = 0.102
                self.cost_km_in = self.cost_km  # no city tax for BEV
                self.cost_m = 0.383
            elif city == "NewYork":
                self.cost_km = 0.080
                self.cost_km_in = self.cost_km
                self.cost_m = 0.429
            elif city == "Shanghai":
                self.cost_km = 0.073
                self.cost_km_in = self.cost_km
                self.cost_m = 0.128

        elif type == "ScooterL":
            self.payload_kg = 905
            self.payload_vol = 7.67 * 1000  # needs to be * 1000 because the volumes in nodes is given with unit m^3 * 10^-3
            self.range_km = 205  # range for BEV is limited
            self.fixed_cost = 47.71 * fixed_cost_bool
            if city == "Paris":
                self.cost_km = 0.073
                self.cost_km_in = self.cost_km  # no city tax for BEV
                self.cost_m = 0.369
            elif city == "NewYork":
                self.cost_km = 0.068
                self.cost_km_in = self.cost_km
                self.cost_m = 0.459
            elif city == "Shanghai":
                self.cost_km = 0.066
                self.cost_km_in = self.cost_km
                self.cost_m = 0.112

        elif type == "ScooterS":
            self.payload_kg = 720
            self.payload_vol = 4.27 * 1000  # needs to be * 1000 because the volumes in nodes is given with unit m^3 * 10^-3
            self.range_km = 119  # range for BEV is limited
            self.fixed_cost = 37.74 * fixed_cost_bool
            if city == "Paris":
                self.cost_km = 0.070
                self.cost_km_in = self.cost_km  # no city tax for BEV
                self.cost_m = 0.369
            elif city == "NewYork":
                self.cost_km = 0.065
                self.cost_km_in = self.cost_km
                self.cost_m = 0.459
            elif city == "Shanghai":
                self.cost_km = 0.064
                self.cost_km_in = self.cost_km
                self.cost_m = 0.112

        elif type == "DouzeV2ECargoBike":
            self.payload_kg = 100
            self.payload_vol = 0.2 * 1000  # needs to be * 1000 because the volumes in nodes is given with unit m^3 * 10^-3
            self.range_km = 128
            self.fixed_cost = 3.5 * fixed_cost_bool
            # self.speed_factor = 0.5  # todo: we have to think about the speed of the bike compared to the other vehicles. Also maybe the unloading speed.
                                     # since driving time and unloading time have a similar power (eg 12 minutes to drive, 10 minutes to unload), we could pretend that the slower speed gets offset by faster unloading
            if city == "Paris":
                self.cost_km = 0.050
                self.cost_km_in = self.cost_km
                self.cost_m = 0.369
            elif city == "NewYork":
                self.cost_km = 0.049
                self.cost_km_in = self.cost_km
                self.cost_m = 0.459
            elif city == "Shanghai":
                self.cost_km = 0.049
                self.cost_km_in = self.cost_km
                self.cost_m = 0.112

        # string vehicle_id # the vehicle id is probably needed to attach the vehicle to a route
        # string vehicle_type # vehicle type is needed to set constraints & prices
        # string vehicle_numberplate # numberplate is my way to connect Vehicles and their Dummy-Vehicles. We will need to get penalty costs over all vehicles with the same numberplate, so they need to know it
        # boolean is_electric # could be used to differentiate between ICEV & BEV. This is important because ICEVs will also need to pass their batterie charge (range) to their dummies. ICEVs can be refuelled.
        #
        # int cost_per_km_inside
        # int cost_per_km_outside
        # int cost_per_min
        # int fixed_cost # fixed costs are used for the uncapped runs which tell us the best fleet mix. In capped runs, they are 0
        #
        # int payload_kg
        # int payload_vol
        # int range # we can use range for both ICEV & BEV
        # int operating_hours


def create_vehicles(city: str, num_Atego: int, num_VWTrans: int, num_VWCaddy: int, num_eFUSO: int,
                    num_eScooterWL: int, num_eScooterWS: int, num_eCargoBike: int, fixed_cost_b: bool) -> list[Vehicle]:
    listOfInitialVehicles = []

    for i in range(num_Atego):
        vehicleType = "MercedesBenzAtego"
        numberplate = "1MBA" + str(i + 1).zfill(3)
        listOfInitialVehicles.append(Vehicle(vehicleType, city, numberplate, fixed_cost_b))
    for i in range(num_VWTrans):
        vehicleType = "VWTransporter"
        numberplate = "2VWT" + str(i + 1).zfill(3)
        listOfInitialVehicles.append(Vehicle(vehicleType, city, numberplate, fixed_cost_b))
    for i in range(num_VWCaddy):
        vehicleType = "VWCaddy"
        numberplate = "3VWC" + str(i + 1).zfill(3)
        listOfInitialVehicles.append(Vehicle(vehicleType, city, numberplate, fixed_cost_b))
    for i in range(num_eFUSO):
        vehicleType = "DeFuso"
        numberplate = "4DeF" + str(i + 1).zfill(3)
        listOfInitialVehicles.append(Vehicle(vehicleType, city, numberplate, fixed_cost_b))
    for i in range(num_eScooterWL):
        vehicleType = "ScooterL"
        numberplate = "5SSL" + str(i + 1).zfill(3)
        listOfInitialVehicles.append(Vehicle(vehicleType, city, numberplate, fixed_cost_b))
    for i in range(num_eScooterWS):
        vehicleType = "ScooterS"
        numberplate = "6SSS" + str(i + 1).zfill(3)
        listOfInitialVehicles.append(Vehicle(vehicleType, city, numberplate, fixed_cost_b))
    for i in range(num_eCargoBike):
        vehicleType = "DouzeV2ECargoBike"
        numberplate = "7ECB" + str(i + 1).zfill(3)
        listOfInitialVehicles.append(Vehicle(vehicleType, city, numberplate, fixed_cost_b))

    return listOfInitialVehicles


""" old stuff """
        # class MercedesBenzAtego:
        #
        #     def __init__(self, plateNum: int):
        #         self.capacity = 2800
        #         self.costs_km = 0.28
        #         self.plateNum = plateNum
        #
        # class VWTransporter:
        #
        #     def __init__(self, plateNum: int):
        #         self.capacity = 883
        #         self.costs_km = 0.16
        #         self.plateNum = plateNum
        #
        #
        # class VWCaddypanelvan:
        #     def __init__(self, plateNum: int):
        #         self.capacity = 670
        #         self.costs_km = 0.13
        #         self.plateNum = plateNum
        #
        #
        # class DaimlerFUSOeCanter:
        #     def __init__(self, plateNum: int):
        #         self.capacity = 2800
        #         self.costs_km = 0.1
        #         self.plateNum = plateNum
        #
        #
        # class StreetScooterWORKL:
        #     def __init__(self, plateNum: int):
        #         self.capacity = 905
        #         self.costs_km = 0.07
        #         self.plateNum = plateNum
        #
        #
        # class StreetScooterWORK:
        #     def __init__(self, plateNum: int):
        #         self.capacity = 720
        #         self.costs_km = 0.07
        #         self.plateNum = plateNum
        #
        #
        # class DouzeV2ECargoBike:
        #     def __init__(self, plateNum: int):
        #         self.capacity = 100
        #         self.costs_km = 0.05
        #         self.plateNum = plateNum
        #
