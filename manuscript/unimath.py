"""Convert the limited inline LaTeX used in the draft into Unicode (renders identically in DOCX and PDF)."""
import re
SUB = {"0":"₀","1":"₁","2":"₂","3":"₃","4":"₄","5":"₅","6":"₆","7":"₇","8":"₈","9":"₉","r":"ᵣ","j":"ⱼ","i":"ᵢ","k":"ₖ","n":"ₙ","p":"ₚ"}
SUP = {"2":"²","*":"*","p":"ᵖ","m":"ᵐ","-":"⁻","1":"¹","0":"⁰","3":"³"}
EXACT = {
 r"\mu \in \mathbb{R}^p \mapsto u(\mu)\in\mathbb{R}^m": "μ ∈ ℝᵖ ↦ u(μ) ∈ ℝᵐ",
 r"\{(\mu_i,u(\mu_i))\}": "{(μᵢ, u(μᵢ))}",
 r"\mathrm{err}=\frac1{n}\sum_j \|\hat u(\mu_j)-u(\mu_j)\|_2/\|u(\mu_j)\|_2": "err = (1/n) Σⱼ ‖û(μⱼ) − u(μⱼ)‖₂ / ‖u(μⱼ)‖₂",
 r"u(\mu)\approx \bar u+V_r a(\mu)": "u(μ) ≈ ū + Vᵣ a(μ)",
 r"y=\log_{10}(\mathrm{err}_{NL^*}/\mathrm{err}_{LS^*})": "y = log₁₀(err_NL* / err_LS*)",
 r"y\sim\log_2N+f_1+f_2": "y ~ log₂N + f₁ + f₂", r"y\sim\log_2N+p": "y ~ log₂N + p",
 r"N\in\{32,64,128,256,512,1024\}": "N ∈ {32, 64, 128, 256, 512, 1024}", r"k\in\{2,4,8,16\}": "k ∈ {2, 4, 8, 16}", r"m\in\{128,256\}": "m ∈ {128, 256}",
 r"[-0.25,1.25]^p": "[−0.25, 1.25]ᵖ", r"10^{-12}\sigma_1": "10⁻¹²σ₁", r"f_1=\log_{10}": "f₁ = log₁₀", r"\log_{10}\sigma_k": "log₁₀σₖ", r"\log_2N": "log₂N",
 r"LS^*": "LS*", r"NL^*": "NL*", r"\bar y": "ȳ", r"\hat u": "û", r"V_r": "Vᵣ", r"L_2": "L₂", r"k\le 10": "k ≤ 10", r"y>0": "y > 0", r"a(\mu)": "a(μ)", r"\mu": "μ", r"f_2": "f₂", r"n_0=32": "n₀ = 32",
}
def conv(m):
    t = m.group(1).strip()
    if t in EXACT: return EXACT[t]
    t = t.replace("=", " = ")
    return re.sub(r"\s+", " ", t).strip()
def unimath(s): return re.sub(r"\$([^$\n]+)\$", conv, s)
