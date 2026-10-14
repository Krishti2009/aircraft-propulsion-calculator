
import math


# ============================================================
# 1. CALCULATION FUNCTIONS
# ============================================================

def calculate_shaft_power(torque_nm, rpm):
    angular_velocity = 2 * math.pi * rpm / 60
    power_watts = torque_nm * angular_velocity
    power_kw = power_watts / 1000
    return power_watts, power_kw


def calculate_electric_motor_power(voltage, current, motor_efficiency):
    electric_power_w = voltage * current
    mechanical_power_w = electric_power_w * motor_efficiency
    return electric_power_w, mechanical_power_w


def calculate_propulsive_power(power_kw, efficiency):
    useful_power_kw = power_kw * efficiency
    return useful_power_kw


def calculate_thrust(useful_power_kw, velocity):
    useful_power_w = useful_power_kw * 1000
    thrust_n = useful_power_w / velocity
    return thrust_n


def calculate_air_density(altitude_m):
    temperature_sea_level = 288.15
    pressure_sea_level = 101325
    temperature_lapse_rate = 0.0065
    gas_constant_air = 287.05
    gravity = 9.80665

    if altitude_m > 11000:
        raise ValueError(
            "This atmospheric model supports altitudes up to 11000 m."
        )

    temperature = (
        temperature_sea_level
        - temperature_lapse_rate * altitude_m
    )

    pressure = pressure_sea_level * (
        temperature / temperature_sea_level
    ) ** (
        gravity / (gas_constant_air * temperature_lapse_rate)
    )

    density = pressure / (gas_constant_air * temperature)

    return temperature, pressure, density


def calculate_dynamic_pressure(air_density, velocity):
    dynamic_pressure = 0.5 * air_density * velocity**2
    return dynamic_pressure


def calculate_lift(dynamic_pressure, wing_area, lift_coefficient):
    lift_n = dynamic_pressure * wing_area * lift_coefficient
    return lift_n


def calculate_drag(air_density, velocity, wing_area, drag_coefficient):
    dynamic_pressure = calculate_dynamic_pressure(
        air_density, velocity
    )
    drag_n = dynamic_pressure * wing_area * drag_coefficient
    return drag_n


def calculate_power_required(drag_n, velocity):
    power_required_w = drag_n * velocity
    power_required_kw = power_required_w / 1000
    return power_required_w, power_required_kw



# ============================================================
# 2. INPUT VALIDATION
# ============================================================

def get_positive_number(prompt, allow_zero=False):
    while True:
        try:
            value = float(input(prompt))

            if not math.isfinite(value):
                print("Invalid input. Enter a finite number.")
                continue

            if value > 0 or (allow_zero and value == 0):
                return value

            print("Invalid value. Please enter a valid positive number.")

        except ValueError:
            print("Invalid input. Please enter a number.")


def get_efficiency(prompt):
    while True:
        efficiency_percent = get_positive_number(prompt)

        if efficiency_percent <= 100:
            return efficiency_percent

        print("Efficiency cannot exceed 100%. Please try again.")



# ============================================================
# 3. AIRCRAFT INPUTS
# ============================================================

print("===================================")
print("    AIRCRAFT PROPULSION CALCULATOR")
print("===================================")

aircraft_name = input("Enter aircraft name: ")

print("\nSelect propulsion type:")
print("1. Piston engine + propeller")
print("2. Electric motor + propeller")

propulsion_types = {
    "1": "propeller_piston",
    "2": "electric_propeller"
  
}

while True:
    choice = input("Enter your choice (1-2): ")

    if choice in propulsion_types:
        propulsion_type = propulsion_types[choice]
        break

    print("Invalid choice. Please select a number between 1 and 2.")


mass = get_positive_number("Enter aircraft mass (kg): ")

altitude = get_positive_number(
    "Enter flight altitude (m): ",
    allow_zero=True
)

velocity = get_positive_number(
    "Enter flight speed (m/s): ",
    allow_zero=True
)

aircraft = {
    "name": aircraft_name,
    "propulsion_type": propulsion_type,
    "mass_kg": mass,
    "altitude_m": altitude,
    "flight_speed_m/s": velocity
}

weight_n = mass * 9.81


# ============================================================
# 4. ATMOSPHERIC CALCULATIONS
# ============================================================

temperature_k, pressure_pa, air_density = calculate_air_density(
    aircraft["altitude_m"]
)

dynamic_pressure = calculate_dynamic_pressure(
    air_density,
    aircraft["flight_speed_m/s"]
)


print("\n===================================")
print("       AIRCRAFT REQUIREMENTS")
print("===================================")

print(f"Aircraft name: {aircraft['name']}")
print(f"Propulsion type: {aircraft['propulsion_type']}")
print(f"Aircraft mass: {mass:.2f} kg")
print(f"Aircraft weight: {weight_n:.2f} N")
print(f"Flight altitude: {altitude:.2f} m")
print(f"Flight speed: {velocity:.2f} m/s")

print("\n--- ATMOSPHERIC CONDITIONS ---")
print(f"Air temperature: {temperature_k:.2f} K")
print(f"Air pressure: {pressure_pa:.2f} Pa")
print(f"Air density: {air_density:.4f} kg/m^3")
print(f"Dynamic pressure: {dynamic_pressure:.2f} Pa")


# ============================================================
# 5. AERODYNAMIC CALCULATIONS
#    Shared by BOTH piston and electric aircraft
# ============================================================

if velocity > 0:

    print("\n--- AERODYNAMIC DATA ---")

    wing_area = get_positive_number("Wing area (m^2): ")
    lift_coefficient = get_positive_number("Lift coefficient: ")

    lift_n = calculate_lift(
        dynamic_pressure,
        wing_area,
        lift_coefficient
    )

    drag_coefficient = get_positive_number("Drag coefficient: ")

    drag_n = calculate_drag(
        air_density,
        velocity,
        wing_area,
        drag_coefficient
    )

    power_required_w, power_required_kw = calculate_power_required(
        drag_n,
        velocity
    )

    print(f"\nWing area: {wing_area:.2f} m^2")
    print(f"Lift coefficient: {lift_coefficient:.3f}")
    print(f"Estimated lift: {lift_n:.2f} N")
    print(f"Drag coefficient: {drag_coefficient:.4f}")

    print("\n--- THRUST AND POWER REQUIRED ---")
    print(f"Estimated drag: {drag_n:.2f} N")
    print(f"Thrust required for steady level flight: {drag_n:.2f} N")
    print(f"Power required: {power_required_w:.2f} W")
    print(f"Power required: {power_required_kw:.3f} kW")

    if lift_n >= weight_n:
        print("Lift check: estimated lift is at least equal to weight.")
    else:
        print("Lift check: estimated lift is less than aircraft weight.")

else:
    wing_area = None
    lift_coefficient = None
    drag_coefficient = None
    lift_n = None
    drag_n = None
    power_required_w = None
    power_required_kw = None

    print("\nAerodynamic estimates unavailable at zero flight speed.")


# ============================================================
# 6. PROPULSION CALCULATIONS
# ============================================================

if propulsion_type == "propeller_piston":

    print("\n--- PISTON ENGINE DATA ---")

    torque = get_positive_number("Engine torque (N m): ")
    rpm = get_positive_number("Engine speed (RPM): ")

    efficiency_percent = get_efficiency(
        "Propeller efficiency (%): "
    )
    efficiency = efficiency_percent / 100

    power_w, power_kw = calculate_shaft_power(torque, rpm)

    useful_power_kw = calculate_propulsive_power(
        power_kw,
        efficiency
    )
    max_rated_power_kw=get_positive_number(
        "Maximum rated engine power(kW)"
    )
    max_rated_rpm=get_positive_number(
        "Maximum rated engine speed(RPM):"
    )

    engine_power_pass=power_kw<=max_rated_power_kw
    engine_rpm_pass=rpm<=max_rated_rpm

    print("\n--- ENGINE LIMIT CHECK ---")
    print(f"Calculated engine power: {power_kw:.2f} kW")
    print(f"Maximum rated power: {max_rated_power_kw:.2f} kW")
    print("Engine power limit:", "PASS" if engine_power_pass else "FAIL")

    print(f"Engine speed: {rpm:.0f} RPM")
    print(f"Maximum rated speed: {max_rated_rpm:.0f} RPM")
    print("Engine RPM limit:", "PASS" if engine_rpm_pass else "FAIL")


    if velocity > 0:
        thrust_n = calculate_thrust(useful_power_kw, velocity)
        print(f"Estimated thrust: {thrust_n:.2f} N")
    else:
        thrust_n = None
        print("Thrust estimate unavailable at zero flight speed.")


elif propulsion_type == "electric_propeller":

    print("\n--- ELECTRIC MOTOR DATA ---")

    voltage = get_positive_number("Battery voltage (V): ")
    current = get_positive_number("Motor current (A): ")

    motor_efficiency_percent = get_efficiency(
        "Motor efficiency (%): "
    )
    motor_efficiency = motor_efficiency_percent / 100

    electrical_power_w, mechanical_power_w = (
        calculate_electric_motor_power(
            voltage,
            current,
            motor_efficiency
        )
    )

    mechanical_power_kw = mechanical_power_w / 1000

    
    max_continuous_current = get_positive_number(
        "Maximum continuous current (A): "
    )

    rated_motor_power_kw = get_positive_number(
        "Rated motor output power (kW): "
    )

    motor_current_pass = current <= max_continuous_current
    motor_power_pass = mechanical_power_kw <= rated_motor_power_kw


    efficiency_percent = get_efficiency(
        "Propeller efficiency (%): "
    )
    efficiency = efficiency_percent / 100

    useful_power_kw = calculate_propulsive_power(
        mechanical_power_kw,
        efficiency
    )

    print("\n--- ELECTRIC PROPULSION PERFORMANCE ---")
    print(f"Battery voltage: {voltage:.2f} V")
    print(f"Motor current: {current:.2f} A")
    print(f"Electrical input power: {electrical_power_w:.2f} W")
    print(f"Motor efficiency: {motor_efficiency_percent:.1f}%")
    print(f"Mechanical output power: {mechanical_power_w:.2f} W")
    print(f"Mechanical output power: {mechanical_power_kw:.3f} kW")
    print(f"Propeller efficiency: {efficiency_percent:.1f}%")
    print(f"Useful propulsive power: {useful_power_kw:.3f} kW")

    if velocity > 0:
        thrust_n = calculate_thrust(useful_power_kw, velocity)
        print(f"Estimated thrust: {thrust_n:.2f} N")
    else:
        thrust_n = None
        print("Thrust estimate unavailable at zero flight speed.")


else:
    print("\nThis propulsion module is not implemented yet.")
    print("Jet engine, rocket, and other models will be added later.")


    print("\n--- MOTOR LIMIT CHECK ---")
    print(
        "Motor current limit:",
        "PASS" if motor_current_pass else "FAIL"
    )
    print(
        "Motor output power limit:",
        "PASS" if motor_power_pass else "FAIL"
    )


# ============================================================
# 7. OVERALL PERFORMANCE CHECK
# ============================================================

print("\n===================================")
print("      OVERALL PERFORMANCE CHECK")
print("===================================")

if velocity <= 0 or lift_n is None or drag_n is None:
    print("FLIGHT PERFORMANCE CHECK: INCOMPLETE")
    print("Positive flight speed and aerodynamic calculations are required.")

else:
    # Flight performance checks
    lift_pass = lift_n >= weight_n
    thrust_pass = thrust_n >= drag_n
    power_pass = useful_power_kw >= power_required_kw

    print("\n--- FLIGHT PERFORMANCE ---")
    print("Lift check:", "PASS" if lift_pass else "FAIL")
    print(f"Available thrust: {thrust_n:.2f} N")
    print(f"Required thrust: {drag_n:.2f} N")
    print("Thrust check:", "PASS" if thrust_pass else "FAIL")
    print(f"Available useful power: {useful_power_kw:.3f} kW")
    print(f"Required power: {power_required_kw:.3f} kW")
    print("Power check:", "PASS" if power_pass else "FAIL")

    # Power margin
    power_margin_kw = useful_power_kw - power_required_kw

    print("\n--- POWER MARGIN ---")
    print(f"Power margin: {power_margin_kw:.3f} kW")

    if power_required_kw > 0:
        margin_percent = (
            power_margin_kw / power_required_kw
        ) * 100
        print(f"Power margin: {margin_percent:.2f}%")
    else:
        print("Power margin percentage: unavailable.")

    # Component limits
    if propulsion_type == "propeller_piston":
        component_pass = engine_power_pass and engine_rpm_pass

        print("\n--- ENGINE LIMITS ---")
        print("Engine power limit:",
              "PASS" if engine_power_pass else "FAIL")
        print("Engine RPM limit:",
              "PASS" if engine_rpm_pass else "FAIL")

    else:
        component_pass = motor_current_pass and motor_power_pass

        print("\n--- MOTOR LIMITS ---")
        print("Motor current limit:",
              "PASS" if motor_current_pass else "FAIL")
        print("Motor output power limit:",
              "PASS" if motor_power_pass else "FAIL")

    # Final result
    if lift_pass and thrust_pass and power_pass and component_pass:
        print("\nOVERALL SYSTEM CHECK: PASS")
        print("All implemented checks passed.")
    else:
        print("\nOVERALL SYSTEM CHECK: FAIL")
        print("One or more checks failed.")

print("\n===================================")
print("          CALCULATION DONE")
print("===================================")
