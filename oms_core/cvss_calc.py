class CVSSCalculator:
    """
    CVSS 3.1 极简计算器
    """
    BASE_SCORES = {
        "AV": {"N": 0.85, "A": 0.62, "L": 0.55, "P": 0.2},  # Attack Vector
        "AC": {"L": 0.77, "H": 0.44},                      # Attack Complexity
        "PR": {                                            # Privileges Required
            "N": {"U": 0.85, "C": 0.85}, 
            "L": {"U": 0.62, "C": 0.68},
            "H": {"U": 0.27, "C": 0.50}
        },
        "UI": {"N": 0.85, "R": 0.62},                      # User Interaction
        "CIA": {"H": 0.56, "L": 0.22, "N": 0}              # Impact (C, I, A)
    }

    @staticmethod
    def calculate(av, ac, pr, ui, s, c, i, a):
        """
        极简公式模拟 (非官方完整版，仅供决策参考)
        s: Scope (U/C)
        """
        impact = 1 - ((1 - CVSSCalculator.BASE_SCORES["CIA"][c]) * 
                      (1 - CVSSCalculator.BASE_SCORES["CIA"][i]) * 
                      (1 - CVSSCalculator.BASE_SCORES["CIA"][a]))
        
        exploitability = 8.22 * CVSSCalculator.BASE_SCORES["AV"][av] * \
                         CVSSCalculator.BASE_SCORES["AC"][ac] * \
                         CVSSCalculator.BASE_SCORES["PR"][pr][s] * \
                         CVSSCalculator.BASE_SCORES["UI"][ui]
        
        base_score = min(10, (1.1 * (impact + exploitability))) if impact > 0 else 0
        return round(base_score, 1)

if __name__ == "__main__":
    # 示例: 远程、低复杂度、无权限、无交互、影响高
    score = CVSSCalculator.calculate("N", "L", "N", "N", "U", "H", "H", "H")
    print(f"CVSS Base Score Estimate: {score}")
