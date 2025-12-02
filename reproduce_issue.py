from pyfluids import HumidAir, InputHumidAir

def test_psychro_meaning():
    P_Pa = 101325
    T_db = 25
    
    # Case A: Input 0.5 (Is this 50% or 0.5%?)
    print("--- Input 0.5 ---")
    ha = HumidAir().with_state(
        InputHumidAir.pressure(P_Pa),
        InputHumidAir.temperature(T_db),
        InputHumidAir.relative_humidity(0.5)
    )
    print(f"w (Humidity Ratio): {ha.humidity}")

    # Case B: Input 50 (Is this 50%?)
    print("\n--- Input 50 ---")
    ha = HumidAir().with_state(
        InputHumidAir.pressure(P_Pa),
        InputHumidAir.temperature(T_db),
        InputHumidAir.relative_humidity(50)
    )
    print(f"w (Humidity Ratio): {ha.humidity}")

if __name__ == "__main__":
    test_psychro_meaning()
