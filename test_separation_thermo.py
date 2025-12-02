
from thermo import Chemical, Mixture
import pandas as pd
import numpy as np

def test_thermo_vle_enthalpy():
    print("Testing Thermo VLE and Enthalpy...")
    
    chem1 = "ethanol"
    chem2 = "water"
    P = 101325.0 # Pa
    
    xs = np.linspace(0.0, 1.0, 11)
    data = []
    
    print(f"Mixture: {chem1}-{chem2} at {P} Pa")
    print(f"{'x1':<10} {'y1':<10} {'T (K)':<10} {'HL (J/mol)':<15} {'HV (J/mol)':<15}")
    
    for x1 in xs:
        x2 = 1.0 - x1
        # Create mixture at bubble point (Vapor fraction = 0)
        try:
            # We need to find the bubble point temperature first
            # thermo's Mixture can do this if we specify VF=0
            mix = Mixture([chem1, chem2], zs=[x1, x2], P=P)
            
            # Calculate bubble point
            # Mixture in thermo automatically calculates equilibrium if T and P are given? 
            # No, we need to solve for T given P and VF=0
            
            # Using flash method
            # Mixture doesn't have a direct 'bubble_point_at_P' method easily accessible without some setup
            # But we can iterate T.
            
            # Actually, let's try setting VF=0 and P=P
            # mix.flash(P=P, VF=0) -> This should find T
            # Define error function for T
            def error_func(T):
                c1 = Chemical(chem1, T=T)
                c2 = Chemical(chem2, T=T)
                p1 = c1.Psat
                p2 = c2.Psat
                if p1 is None or p2 is None: return 1e9
                return x1 * p1 + x2 * p2 - P
            
            from scipy.optimize import fsolve
            # Guess T (boiling point of pure components weighted)
            tb1 = Chemical(chem1).Tb
            tb2 = Chemical(chem2).Tb
            t_guess = x1*tb1 + x2*tb2
            
            t_sol = fsolve(error_func, t_guess)[0]
            
            # Calculate y1
            c1_sol = Chemical(chem1, T=t_sol)
            y1 = x1 * c1_sol.Psat / P
            
            # Enthalpies
            # Liquid Enthalpy: x1*H1_L + x2*H2_L + H_excess (ignore excess for now)
            # Vapor Enthalpy: y1*H1_V + y2*H2_V
            
            # Chemical.H is Enthalpy in J/mol
            # We need to make sure we get the phase right.
            # Chemical(..., phase='l').H
            
            h1_l = Chemical(chem1, T=t_sol, P=P).H
            h2_l = Chemical(chem2, T=t_sol, P=P).H # P is total pressure, technically should be partial but for liquid H effect is small
            
            # Inspect object
            if x1 == 0.0:
                c_test = Chemical(chem1, T=t_sol, P=P)
                # print([d for d in dir(c_test) if 'H' in d])
            
            # Hm is molar enthalpy?
            # Let's try to use H for liquid (since it's bubble point)
            h1_l = Chemical(chem1, T=t_sol, P=P).H
            h2_l = Chemical(chem2, T=t_sol, P=P).H
            
            # For vapor enthalpy, we need the enthalpy of the component as a gas at T, P.
            # If T < Tb, it's liquid. We need hypothetical gas or real gas if it could exist.
            # Actually, in the mixture, the partial pressure is y*P.
            # So maybe Chemical(chem1, T=t_sol, P=y1*P).H ?
            # If y1*P < Psat, it is gas.
            
            h1_v = Chemical(chem1, T=t_sol, P=y1*P if y1 > 1e-9 else 100).H 
            h2_v = Chemical(chem2, T=t_sol, P=(1-y1)*P if (1-y1) > 1e-9 else 100).H
            
            # Enthalpy of mixture (Ideal)
            HL = x1 * h1_l + x2 * h2_l
            HV = y1 * h1_v + (1-y1) * h2_v
            
            print(f"{x1:<10.2f} {y1:<10.2f} {t_sol:<10.2f} {HL:<15.2f} {HV:<15.2f}")
            
        except Exception as e:
            print(f"Error at x1={x1}: {e}")

if __name__ == "__main__":
    test_thermo_vle_enthalpy()
