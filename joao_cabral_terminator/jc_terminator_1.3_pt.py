#!/usr/bin/env python3
"""
Ficha de Química para TI-Nspire CX II-T
========================================
Execução:  python3 jc_terminator_1.3_pt.py  (na calculadora ou computador)

INFRAESTRUTURA:
---------------
Este programa usa uma arquitetura modular, orientada a dados, para fácil personalização:

1. CAMADA DE DADOS (topo do ficheiro):
   - TOPICS: Dicionário definindo entradas do menu principal (rótulo, chave, conteúdo/função)
   - SUBTOPICS: Dicionários aninhados para conteúdo de submenus
   - RADII_DATA: Base de dados de raios dos elementos
   - Todo o conteúdo armazenado em dados estruturados, não em strings hardcoded

2. CAMADA DE LÓGICA (funções):
   - show_topic(topic_key): Exibição genérica para tópicos de texto simples
   - show_interactive(topic_key): Dispatcher para calculadoras interativas
   - show_submenu(parent_key, submenu_dict): Manipulador genérico de submenus
   - find_ec(): Busca de configuração eletrónica (símbolo, Z, ou nome)
   - parse_species(): Parse de formato "Fe2+", "O-2"

3. CAMADA DE APRESENTAÇÃO:
   - main(): Loop do menu principal usando dicionário TOPICS
   - Loops de submenu usando dicionários SUBTOPICS
   - Helpers de formatação consistentes

GUIA DE PERSONALIZAÇÃO:
-----------------------
Para adicionar um novo tópico principal:
  1. Adicionar entrada ao dicionário TOPICS com: key, label, type ('text'|'interactive'|'submenu'), content
  2. Se 'submenu', adicionar entrada correspondente ao dicionário SUBTOPICS
  3. Se 'interactive', adicionar handler em show_interactive()

Para adicionar uma entrada de submenu:
  1. Adicionar a SUBTOPICS[parent_key] com key, label, content
  2. Content pode ser string (exibida) ou callable (executada)

Para modificar geometria molecular (13 entradas):
  1. Editar dicionário MOLECULAR_GEOMETRY_SUBTOPICS abaixo
  2. Cada entrada: key -> {label, content, [sub_submenu]}
  3. Content suporta {variáveis} para valores dinâmicos
"""

# ============================================================================
# CONFIGURAÇÃO - PERSONALIZE ESTES VALORES
# ============================================================================

# --- Tópicos do Menu Principal ---
# type: 'text' (imprime conteúdo), 'interactive' (chama função), 'submenu' (mostra submenu)
TOPICS = {
    "1":  {"key": "constants",    "label": "Constantes Físicas",           "type": "text",      "content": "CONSTANTS"},
    "2":  {"key": "quantum",      "label": "Fórmulas Quânticas",           "type": "text",      "content": "QUANTUM"},
    "3":  {"key": "exceptions",   "label": "Exceções da CE",               "type": "text",      "content": "EXCEPTIONS"},
    "4":  {"key": "config",       "label": "Consultar CE",                 "type": "interactive", "content": "show_config"},
    "5":  {"key": "all_ec",       "label": "Todas as 118 CE",              "type": "text",      "content": "ALL_EC"},
    "6":  {"key": "trends",       "label": "Tendências Periódicas",        "type": "text",      "content": "TRENDS"},
    "7":  {"key": "stoich",       "label": "Estequiometria",               "type": "text",      "content": "STOICH"},
    "8":  {"key": "modelos",      "label": "Modelos Atómicos (PT)",        "type": "text",      "content": "MODELOS"},
    "9":  {"key": "algoritmos",   "label": "Algoritmos (PT)",              "type": "text",      "content": "ALGORITMOS"},
    "10": {"key": "radii",        "label": "Calculadora Raios Atómicos/Iónicos", "type": "interactive", "content": "show_radii"},
    "11": {"key": "molecular",    "label": "Ligação, Geometria e Ângulos", "type": "submenu",   "content": "MOLECULAR"},
    "q":  {"key": "quit",         "label": "Sair",                         "type": "quit",      "content": None},
}

# --- Definições de Submenus ---
# Cada submenu é um dict: key -> {label, content, [sub_submenu]}
# content pode ser: string (impressa), callable (executada), ou dict (submenu aninhado)

# Geometria Molecular - 13 Entradas Personalizáveis
# PERSONALIZE: Adicione/modifique entradas aqui. Cada entrada suporta:
#   - label: exibido no menu
#   - content: string para imprimir (use {var} para valores dinâmicos)
#   - submenu: submenu aninhado opcional
#   - vars: dict opcional de variáveis para formatação do content
MOLECULAR_GEOMETRY_SUBTOPICS = {
    "1":  {"label": "Teoria VSEPR - Básico",           "content": "VSEPR_BASICS"},
    "2":  {"label": "Linear (AX₂)",                    "content": "GEOM_LINEAR",       "vars": {"angle": "180°", "examples": "CO₂, BeCl₂, HgCl₂"}},
    "3":  {"label": "Trigonal Planar (AX₃)",           "content": "GEOM_TRIG_PLANAR",  "vars": {"angle": "120°", "examples": "BF₃, SO₃, NO₃⁻"}},
    "4":  {"label": "Tetraédrica (AX₄)",               "content": "GEOM_TETRAHEDRAL",  "vars": {"angle": "109,5°", "examples": "CH₄, CCl₄, NH₄⁺"}},
    "5":  {"label": "Bipiramidal Trigonal (AX₅)",      "content": "GEOM_TRIG_BIPYR",   "vars": {"angles": "90°, 120°", "examples": "PCl₅, PF₅"}},
    "6":  {"label": "Octaédrica (AX₆)",                "content": "GEOM_OCTAHEDRAL",   "vars": {"angle": "90°", "examples": "SF₆, [Co(NH₃)₆]³⁺"}},
    "7":  {"label": "Angular / Dobrada (AX₂E)",        "content": "GEOM_BENT",         "vars": {"angle": "~104,5°", "examples": "H₂O, SO₂, O₃"}},
    "8":  {"label": "Piramidal Trigonal (AX₃E)",       "content": "GEOM_TRIG_PYRAM",   "vars": {"angle": "~107°", "examples": "NH₃, PCl₃"}},
    "9":  {"label": "Tipo Serra / See-Saw (AX₄E)",     "content": "GEOM_SEESAW",       "vars": {"angles": "90°, 120°, 180°", "examples": "SF₄"}},
    "10": {"label": "Em T / T-Shaped (AX₃E₂)",         "content": "GEOM_T_SHAPED",     "vars": {"angles": "90°, 180°", "examples": "ClF₃"}},
    "11": {"label": "Piramidal Quadrada (AX₅E)",       "content": "GEOM_SQ_PYRAM",     "vars": {"angle": "90°", "examples": "BrF₅, XeOF₄"}},
    "12": {"label": "Planar Quadrada (AX₄E₂)",         "content": "GEOM_SQ_PLANAR",    "vars": {"angle": "90°", "examples": "XeF₄, [Ni(CN)₄]²⁻"}},
    "13": {"label": "Referência de Hibridização",      "content": "HYBRIDIZATION_REF"},
    "b":  {"label": "Voltar ao Menu Principal",        "content": "BACK"},
}

# Submenu Calculadora de Raios
RADII_SUBTOPICS = {
    "1": {"label": "Consultar Raio",       "content": "radius_lookup"},
    "2": {"label": "Comparar Duas Espécies","content": "radius_compare"},
    "3": {"label": "Estimar por Tendência","content": "radius_estimate"},
    "b": {"label": "Voltar",               "content": "BACK"},
}

# Mapeia chaves de submenu às suas definições
SUBTOPICS = {
    "MOLECULAR": MOLECULAR_GEOMETRY_SUBTOPICS,
    "RADII": RADII_SUBTOPICS,
}

# ============================================================================
# STRINGS DE CONTEÚDO - PERSONALIZE ESTAS
# ============================================================================

CONSTANTS = """CONSTANTES FÍSICAS & FATORES DE CONVERSÃO

- Constante de Planck:           h = 6,63e-34 J·s
- Velocidade da luz:             c = 3,00e8 m/s
- Número de Avogadro:            N_A = 6,022e23 mol⁻¹
- Massa do electrão:             m_e = 9,11e-31 kg
- Electrão-volt:                 1 eV = 1,60e-19 J
- Nível de energia do H:         E_n = -2,18e-18 × (Z² / n²) J
- Constante de Rydberg:          R_H = 1,097e7 m⁻¹
- Constante dos gases:           R = 8,314 J/mol·K = 0,08206 L·atm/mol·K
- Constante de Faraday:          F = 96485 C/mol
- Pressão padrão:                1 atm = 101,325 kPa = 760 mmHg
- Temperatura padrão:            0°C = 273,15 K
"""

QUANTUM = """MODELO ATÓMICO & FÓRMULAS DE MECÂNICA QUÂNTICA

Energia do Fotão:
  E = h·f = h·c/λ

Transições de Energia:
  ΔE = E_final - E_inicial = E_fotão

Efeito Fotoeléctrico / Fotoionização:
  E_fotão = E_rem + E_kinetic

Energia Cinética:
  E_kin = ½·m·v²

Comprimento de Onda de De Broglie:
  λ = h / (m·v)

Números Quânticos:
  n ≥ 1              (nível principal / energia & tamanho)
  l = 0 a n-1        (subnível: s=0, p=1, d=2, f=3)
  m_l = -l a +l      (orbitais = 2l + 1)
  m_s = +½ ou -½     (spin)

  Total de orbitais no nível n = n²
  Máx. electrões no nível n = 2n²
"""

# Configurações Electrónicas (Z, config)
EC = {
    "H":  (1,  "1s¹"),        "He": (2,  "1s²"),
    "Li": (3,  "[He] 2s¹"),   "Be": (4,  "[He] 2s²"),
    "B":  (5,  "[He] 2s² 2p¹"), "C": (6,  "[He] 2s² 2p²"),
    "N":  (7,  "[He] 2s² 2p³"), "O": (8,  "[He] 2s² 2p⁴"),
    "F":  (9,  "[He] 2s² 2p⁵"), "Ne": (10, "[He] 2s² 2p⁶"),
    "Na": (11, "[Ne] 3s¹"),   "Mg": (12, "[Ne] 3s²"),
    "Al": (13, "[Ne] 3s² 3p¹"), "Si": (14, "[Ne] 3s² 3p²"),
    "P":  (15, "[Ne] 3s² 3p³"), "S": (16, "[Ne] 3s² 3p⁴"),
    "Cl": (17, "[Ne] 3s² 3p⁵"), "Ar": (18, "[Ne] 3s² 3p⁶"),
    "K":  (19, "[Ar] 4s¹"),   "Ca": (20, "[Ar] 4s²"),
    "Sc": (21, "[Ar] 3d¹ 4s²"), "Ti": (22, "[Ar] 3d² 4s²"),
    "V":  (23, "[Ar] 3d³ 4s²"), "Cr": (24, "[Ar] 3d⁵ 4s¹"),
    "Mn": (25, "[Ar] 3d⁵ 4s²"), "Fe": (26, "[Ar] 3d⁶ 4s²"),
    "Co": (27, "[Ar] 3d⁷ 4s²"), "Ni": (28, "[Ar] 3d⁸ 4s²"),
    "Cu": (29, "[Ar] 3d¹⁰ 4s¹"), "Zn": (30, "[Ar] 3d¹⁰ 4s²"),
    "Ga": (31, "[Ar] 3d¹⁰ 4s² 4p¹"), "Ge": (32, "[Ar] 3d¹⁰ 4s² 4p²"),
    "As": (33, "[Ar] 3d¹⁰ 4s² 4p³"), "Se": (34, "[Ar] 3d¹⁰ 4s² 4p⁴"),
    "Br": (35, "[Ar] 3d¹⁰ 4s² 4p⁵"), "Kr": (36, "[Ar] 3d¹⁰ 4s² 4p⁶"),
    "Rb": (37, "[Kr] 5s¹"),   "Sr": (38, "[Kr] 5s²"),
    "Y":  (39, "[Kr] 4d¹ 5s²"), "Zr": (40, "[Kr] 4d² 5s²"),
    "Nb": (41, "[Kr] 4d⁴ 5s¹"), "Mo": (42, "[Kr] 4d⁵ 5s¹"),
    "Tc": (43, "[Kr] 4d⁵ 5s²"), "Ru": (44, "[Kr] 4d⁷ 5s¹"),
    "Rh": (45, "[Kr] 4d⁸ 5s¹"), "Pd": (46, "[Kr] 4d¹⁰"),
    "Ag": (47, "[Kr] 4d¹⁰ 5s¹"), "Cd": (48, "[Kr] 4d¹⁰ 5s²"),
    "In": (49, "[Kr] 4d¹⁰ 5s² 5p¹"), "Sn": (50, "[Kr] 4d¹⁰ 5s² 5p²"),
    "Sb": (51, "[Kr] 4d¹⁰ 5s² 5p³"), "Te": (52, "[Kr] 4d¹⁰ 5s² 5p⁴"),
    "I":  (53, "[Kr] 4d¹⁰ 5s² 5p⁵"), "Xe": (54, "[Kr] 4d¹⁰ 5s² 5p⁶"),
    "Cs": (55, "[Xe] 6s¹"),   "Ba": (56, "[Xe] 6s²"),
    "La": (57, "[Xe] 5d¹ 6s²"), "Ce": (58, "[Xe] 4f¹ 5d¹ 6s²"),
    "Pr": (59, "[Xe] 4f³ 6s²"), "Nd": (60, "[Xe] 4f⁴ 6s²"),
    "Pm": (61, "[Xe] 4f⁵ 6s²"), "Sm": (62, "[Xe] 4f⁶ 6s²"),
    "Eu": (63, "[Xe] 4f⁷ 6s²"), "Gd": (64, "[Xe] 4f⁷ 5d¹ 6s²"),
    "Tb": (65, "[Xe] 4f⁹ 6s²"), "Dy": (66, "[Xe] 4f¹⁰ 6s²"),
    "Ho": (67, "[Xe] 4f¹¹ 6s²"), "Er": (68, "[Xe] 4f¹² 6s²"),
    "Tm": (69, "[Xe] 4f¹³ 6s²"), "Yb": (70, "[Xe] 4f¹⁴ 6s²"),
    "Lu": (71, "[Xe] 4f¹⁴ 5d¹ 6s²"), "Hf": (72, "[Xe] 4f¹⁴ 5d² 6s²"),
    "Ta": (73, "[Xe] 4f¹⁴ 5d³ 6s²"), "W":  (74, "[Xe] 4f¹⁴ 5d⁴ 6s²"),
    "Re": (75, "[Xe] 4f¹⁴ 5d⁵ 6s²"), "Os": (76, "[Xe] 4f¹⁴ 5d⁶ 6s²"),
    "Ir": (77, "[Xe] 4f¹⁴ 5d⁷ 6s²"), "Pt": (78, "[Xe] 4f¹⁴ 5d⁹ 6s¹"),
    "Au": (79, "[Xe] 4f¹⁴ 5d¹⁰ 6s¹"), "Hg": (80, "[Xe] 4f¹⁴ 5d¹⁰ 6s²"),
    "Tl": (81, "[Xe] 4f¹⁴ 5d¹⁰ 6s² 6p¹"), "Pb": (82, "[Xe] 4f¹⁴ 5d¹⁰ 6s² 6p²"),
    "Bi": (83, "[Xe] 4f¹⁴ 5d¹⁰ 6s² 6p³"), "Po": (84, "[Xe] 4f¹⁴ 5d¹⁰ 6s² 6p⁴"),
    "At": (85, "[Xe] 4f¹⁴ 5d¹⁰ 6s² 6p⁵"), "Rn": (86, "[Xe] 4f¹⁴ 5d¹⁰ 6s² 6p⁶"),
    "Fr": (87, "[Rn] 7s¹"),   "Ra": (88, "[Rn] 7s²"),
    "Ac": (89, "[Rn] 6d¹ 7s²"), "Th": (90, "[Rn] 6d² 7s²"),
    "Pa": (91, "[Rn] 5f² 6d¹ 7s²"), "U":  (92, "[Rn] 5f³ 6d¹ 7s²"),
    "Np": (93, "[Rn] 5f⁴ 6d¹ 7s²"), "Pu": (94, "[Rn] 5f⁶ 7s²"),
    "Am": (95, "[Rn] 5f⁷ 7s²"), "Cm": (96, "[Rn] 5f⁷ 6d¹ 7s²"),
    "Bk": (97, "[Rn] 5f⁹ 7s²"), "Cf": (98, "[Rn] 5f¹⁰ 7s²"),
    "Es": (99, "[Rn] 5f¹¹ 7s²"), "Fm": (100, "[Rn] 5f¹² 7s²"),
    "Md": (101, "[Rn] 5f¹³ 7s²"), "No": (102, "[Rn] 5f¹⁴ 7s²"),
    "Lr": (103, "[Rn] 5f¹⁴ 7s² 7p¹"), "Rf": (104, "[Rn] 5f¹⁴ 6d² 7s²"),
    "Db": (105, "[Rn] 5f¹⁴ 6d³ 7s²"), "Sg": (106, "[Rn] 5f¹⁴ 6d⁴ 7s²"),
    "Bh": (107, "[Rn] 5f¹⁴ 6d⁵ 7s²"), "Hs": (108, "[Rn] 5f¹⁴ 6d⁶ 7s²"),
    "Mt": (109, "[Rn] 5f¹⁴ 6d⁷ 7s²"), "Ds": (110, "[Rn] 5f¹⁴ 6d⁸ 7s²"),
    "Rg": (111, "[Rn] 5f¹⁴ 6d⁹ 7s²"), "Cn": (112, "[Rn] 5f¹⁴ 6d¹⁰ 7s²"),
    "Nh": (113, "[Rn] 5f¹⁴ 6d¹⁰ 7s² 7p¹"), "Fl": (114, "[Rn] 5f¹⁴ 6d¹⁰ 7s² 7p²"),
    "Mc": (115, "[Rn] 5f¹⁴ 6d¹⁰ 7s² 7p³"), "Lv": (116, "[Rn] 5f¹⁴ 6d¹⁰ 7s² 7p⁴"),
    "Ts": (117, "[Rn] 5f¹⁴ 6d¹⁰ 7s² 7p⁵"), "Og": (118, "[Rn] 5f¹⁴ 6d¹⁰ 7s² 7p⁶"),
}

EXCEPTIONS = """CONFIGURAÇÕES ELECTRÓNICAS & EXCEÇÕES

Exceções de Preenchimento (estabilidade bloco d):
  Cr (Z=24): [Ar] 3d⁵ 4s¹
  Cu (Z=29): [Ar] 3d¹⁰ 4s¹
  Mo (Z=42): [Kr] 4d⁵ 5s¹
  Ag (Z=47): [Kr] 4d¹⁰ 5s¹

Regra de Formação de Catiões:
  Remover electrões s PRIMEIRO, depois d

  Exemplos:
    Fe²⁺  = [Ar] 3d⁶
    Cu⁺   = [Ar] 3d¹⁰
    Ir³⁺  = [Xe] 4f¹⁴ 5d⁶
    Cr³⁺  = [Ar] 3d³
    Mn²⁺  = [Ar] 3d⁵
    Zn²⁺  = [Ar] 3d¹⁰
"""

TRENDS = """TENDÊNCIAS PERIÓDICAS & REGRAS TEÓRICAS

Série isoeletrónica:
  Mesmo nº de e⁻ → raio decresce qnd Z cresce

Raio Atómico vs Iónico:
  Catião < Neutro < Anião
  NO GRUPO: aumenta de cima para baixo
  NO PERÍODO: diminui da esquerda para a direita

Salto de Ionização de Núcleo:
  Grande salto em Iₙ = remover electrão de núcleo (n menor)

Exceções da 1ª Ionização:
  N > O (P > S): repulsão de emparelhamento em orbital p preenchido
  Mg > Al: Al 3p¹ menos penetrante que Mg 3s²

Constância do Bloco d:
  raio & energia de ionização 1 baixa variação
  (forte blindagem d, ΔZ_eff ~ 0,15)

Pontos de Fusão:
  E_ret ∝ (|q₁·q₂|) / (r₊ + r₋)
  cargas mais altas, raio menor = alto ponto de fusão

Termodinâmica em Fase Gasosa:
  ionização (X → X⁺ + e⁻):         endotérmica (ΔH > 0)
  captura de electrão (X + e⁻ → X⁻):   exotérmica (ΔH < 0)
  captura de anião (X⁻ + e⁻ → X²⁻):   endotérmica (repulsão)
"""

STOICH = """ESTEQUIOMETRIA & FÓRMULAS INDUSTRIAIS

Factor de Diluição:
  f = Cᵢ / C_f = V_f / Vᵢ

Rendimento Percentual:
  η = (n_real / n_teórico) × 100

Excesso Percentual:
  %E = ((n_admitido - n_estequiométrico) / n_estequiométrico) × 100

Densidade & Concentração de Solução:
  C = (%m/m × ρ) / M
  C = molaridade (mol/L), ρ = densidade (g/mL), M = massa molar (g/mol)

Reagente Limitante:
  Comparar n_disponível / coef; menor vence

Molalidade:
  m = mol soluto / kg solvente

Fracção Molar:
  X_A = n_A / n_total

Pressão Parcial:
  P_A = X_A × P_total

Lei dos Gases Ideais:
  PV = nRT
"""

MODELOS = """MODELOS ATÓMICOS E MODELOS TEÓRICOS DE RESPOSTA ABERTA

- Thomson: esfera neutra de carga positiva uniforme com electrões encastrados.
  Determinou q/m nos raios catódicos.

- Millikan: determinou a carga do electrão na experiência das gotas de óleo.

- Rutherford (Folha de Ouro): a maioria das partículas alfa passa sem desvio;
  poucas sofrem desvio > 90°. Conclusão: o átomo é espaço vazio com núcleo
  reduzido, denso e positivo.

- Bohr: órbitas circulares estacionárias quantizadas.
  Falha por violar o Princípio de Incerteza de Heisenberg e não explicar
  átomos polieletrónicos.

- Ligação Metálica e Propriedades: rede 3D de cernes positivos imersos num
  mar de electrões deslocalizados. A ligação não-direcional permite o
  deslizamento de planos de cernes sob tensão sem repulsão, garantindo
  ductilidade e maleabilidade.

- Exceções de Ionização (I₁):
  * Al vs Mg: Al (3p¹) é menos penetrante, mais energético e blindado
    pelos electrões 3s² do Mg.
  * O vs N: O (2p⁴) tem um par emparelhado na orbital 2p, gerando
    repulsões intereletrónicas que facilitam a remoção face ao subnível
    2p³ semipreenchido do N.

- Bloco d: variação de raio e I₁ mínima devido à forte blindagem dos
  electrões d internos (ΔZ_ef ~ 0,15). Na ionização de metais de
  transição, os electrões s de maior n são sempre removidos em primeiro lugar.

- Séries Isoeletrónicas: mesmo número de electrões → o raio diminui com
  o aumento de Z devido ao aumento da atracção nuclear efectiva.

- Termodinâmica em Fase Gasosa:
  * Remoção de e⁻ (ionização): Endotérmica (ΔH > 0).
  * Captura por átomo neutro ou catião: Exotérmica (ΔH < 0).
  * Captura por anião (formação de iões dinegativos): Endotérmica
    (ΔH > 0) por repulsão electrostática.

- Energia Reticular e Pontos de Fusão:
  E_ret ∝ (|q₁ × q₂|) / (r₊ + r₋).
  Cargas maiores e raios menores = maior ponto de fusão.
"""

ALGORITMOS = """ALGORITMOS DE CÁLCULO PASSO A PASSO

- Transições de Hidrogénio:
  1) E_fotão = h·c/λ
  2) Identificar n_f pela região (UV→1, Visível→2, IR→3)
  3) E_f = -2,18e-18 / n_f²
  4) E_i = E_f + E_fotão
  5) n_i = √(-2,18e-18 / E_i)

- Diluição e Densidade de Ácido Concentrado:
  1) n_soluto = C_dil × V_dil
  2) m_soluto = n × M
  3) m_solução = m_soluto / (%m/m / 100)
  4) ρ = m_solução / V_conc

- Reações Multietapa com Minérios:
    LEMBRAR QUE O Fe₂O₃ QUE REAGE NA REAÇÃO 2 VEM DE DUAS FONTES;
    O QUE JÁ EXISTIA + O QUE FOI PRODUZIDO NA REAÇÃO 1

    1) converter tudo para moles
        calcule a m pura de cada componente a partir
        da massa do minério e das % m/m
        divide pelas M para ter n inicial e n obtido
    2) Calcular o produzido na reação 1
    3) somar o da reação 1 mais o que já existia
    4) fazer estequiometria

- Reatores Gasosos com Ar Húmido e Excesso:
  1) Fixar Base de Cálculo (ex.: 100 mol do reagente)
  2) n_O₂_admitido = n_O₂_estequiométrico × (1 + %Excesso / 100)
  3) Calcular N₂_entrada = n_O₂_admitido × (%N₂ / %O₂) e H₂O do ar húmido
  4) Aplicar taxa de conversão (α) para achar reagentes consumidos,
     produtos e não reagidos
  5) Fazer balanço molar total da saída (n_total_saída)
  6) Calcular a fracção molar x_i = n_i / n_total_saída
"""

# --- Conteúdo de Geometria Molecular ---
VSEPR_BASICS = """TEORIA VSEPR - BÁSICO

Repulsão dos Pares Electrónicos da Camada de Valência (VSEPR) prevê geometria
molecular baseada na repulsão entre domínios electrónicos (pares de ligação + pares isolados).

Geometria de Domínios Electrónicos → Geometria Molecular:
  2 domínios: Linear → Linear
  3 domínios: Trigonal Planar → Trigonal Planar (0 isolados) ou Angular (1 isolado)
  4 domínios: Tetraédrica → Tetraédrica (0), Piramidal Trigonal (1), Angular (2)
  5 domínios: Bipiramidal Trigonal → 5 formas (ver menu)
  6 domínios: Octaédrica → Octaédrica (0), Piramidal Quadrada (1), Planar Quadrada (2)

Princípios-Chave:
1. Pares isolados ocupam mais espaço que pares de ligação
2. Ordem de repulsão: PI-PI > PI-PL > PL-PL
3. Em bipiramidal trigonal: pares isolados preferem posições equatoriais
4. Ângulos ideais reduzidos por repulsão de pares isolados

Notação: AXₙEₘ
  A = átomo central, X = átomos ligados, E = pares isolados
  n + m = total de domínios electrónicos (número estérico)
"""

GEOM_LINEAR = """LINEAR (AX₂) — {angle}

Domínios electrónicos: 2 (0 pares isolados)
Hibridização: sp
Exemplos: {examples}

Todos os ângulos de ligação: 180°
Simetria: D∞h (homonuclear) / C∞v (heteronuclear)
Momento dipolar: Zero (se simétrico)
"""

GEOM_TRIG_PLANAR = """TRIGONAL PLANAR (AX₃) — {angle}

Domínios electrónicos: 3 (0 pares isolados)
Hibridização: sp²
Exemplos: {examples}

Todos os ângulos de ligação: 120°
Simetria: D₃h
Momento dipolar: Zero (se simétrico)
Todos os átomos no mesmo plano
"""

GEOM_TETRAHEDRAL = """TETRAÉDRICA (AX₄) — {angle}

Domínios electrónicos: 4 (0 pares isolados)
Hibridização: sp³
Exemplos: {examples}

Todos os ângulos de ligação: 109,5°
Simetria: T_d
Momento dipolar: Zero (se simétrico)
"""

GEOM_TRIG_BIPYR = """BIPRAMIDAL TRIGONAL (AX₅) — {angles}

Domínios electrónicos: 5 (0 pares isolados)
Hibridização: sp³d
Exemplos: {examples}

Posições:
  • 3 equatoriais (120° entre si) — mais espaço
  • 2 axiais (90° às equatoriais) — menos espaço
Ângulos: 90° (ax-eq), 120° (eq-eq), 180° (ax-ax)
Pares isolados (se houver) preferem equatoriais
"""

GEOM_OCTAHEDRAL = """OCTAÉDRICA (AX₆) — {angle}

Domínios electrónicos: 6 (0 pares isolados)
Hibridização: sp³d²
Exemplos: {examples}

Todas as posições equivalentes
Todos os ângulos: 90° (adjacentes), 180° (opostos)
Simetria: O_h
"""

GEOM_BENT = """ANGULAR / DOBRADA (AX₂E) — {angle}

Domínios electrónicos: 3 (1 par isolado)
Geometria electrónica: Trigonal Planar
Hibridização: sp²
Exemplos: {examples}

Par isolado comprime ângulo de 120°
Ângulo típico: 104,5° (H₂O), ~119° (SO₂)
Molécula polar (dipolo líquido)
"""

GEOM_TRIG_PYRAM = """PIRAMIDAL TRIGONAL (AX₃E) — {angle}

Domínios electrónicos: 4 (1 par isolado)
Geometria electrónica: Tetraédrica
Hibridização: sp³
Exemplos: {examples}

Par isolado comprime ângulo de 109,5°
Ângulo típico: ~107° (NH₃)
Molécula polar (dipolo líquido)
"""

GEOM_SEESAW = """TIPO SERRA / SEE-SAW (AX₄E) — {angles}

Domínios electrónicos: 5 (1 par isolado)
Geometria electrónica: Bipiramidal Trigonal
Hibridização: sp³d
Exemplos: {examples}

Par isolado ocupa posição equatorial
Ângulos: ~90°, ~120°, ~180° (distorcidos)
Molécula polar
"""

GEOM_T_SHAPED = """EM T / T-SHAPED (AX₃E₂) — {angles}

Domínios electrónicos: 5 (2 pares isolados)
Geometria electrónica: Bipiramidal Trigonal
Hibridização: sp³d
Exemplos: {examples}

Ambos pares isolados equatoriais
Ângulos: ~90°, ~180°
Molécula polar
"""

GEOM_SQ_PYRAM = """PIRAMIDAL QUADRADA (AX₅E) — {angle}

Domínios electrónicos: 6 (1 par isolado)
Geometria electrónica: Octaédrica
Hibridização: sp³d²
Exemplos: {examples}

Par isolado ocupa um vértice
Base: planar quadrada (90°)
Ápice à base: ~90° (ligeiramente menos)
Molécula polar
"""

GEOM_SQ_PLANAR = """PLANAR QUADRADA (AX₄E₂) — {angle}

Domínios electrónicos: 6 (2 pares isolados)
Geometria electrónica: Octaédrica
Hibridização: sp³d²
Exemplos: {examples}

Pares isolados opostos (trans) — minimiza repulsão PI-PI
Todos os ângulos de ligação: 90°
Simetria: D₄h
Não polar (se ligantes simétricos)
"""

HYBRIDIZATION_REF = """REFERÊNCIA DE HIBRIDIZAÇÃO

Número Estérico → Hibridização → Geometria Electrónica
──────────────────────────────────────────────────────
2 → sp        → Linear
3 → sp²       → Trigonal Planar
4 → sp³       → Tetraédrica
5 → sp³d      → Bipiramidal Trigonal
6 → sp³d²     → Octaédrica

Determinação Rápida:
1. Contar ligações σ + pares isolados no átomo central = número estérico
2. Correspondência à hibridização acima
3. Prever geometria a partir dos domínios electrónicos

Exemplos Comuns:
  sp:   BeCl₂, CO₂, C₂H₂
  sp²:  BF₃, C₂H₄, SO₃, NO₃⁻
  sp³:  CH₄, NH₃, H₂O, CCl₄
  sp³d: PCl₅, SF₄, ClF₃
  sp³d²: SF₆, XeF₄, BrF₅

Nota: participação de orbitais d debatida para grupo principal;
      sp³d/sp³d² útil para previsão independentemente.
"""

# --- Dados da Calculadora de Raios ---
RADII_DATA = {
    "H":  (53,  {1: 0, -1: 154}),   "He": (31,  {}),
    "Li": (167, {1: 76}),           "Be": (112, {2: 45}),
    "B":  (87,  {3: 27}),           "C":  (67,  {4: 16, -4: 260}),
    "N":  (56,  {3: 16, -3: 146}),  "O":  (48,  {-2: 140}),
    "F":  (42,  {-1: 133}),         "Ne": (38,  {}),
    "Na": (190, {1: 102}),          "Mg": (145, {2: 72}),
    "Al": (118, {3: 53}),           "Si": (111, {4: 40, -4: 271}),
    "P":  (106, {3: 44, -3: 212}),  "S":  (102, {2: 84, -2: 184}),
    "Cl": (99,  {1: 181, -1: 181}), "Ar": (71,  {}),
    "K":  (243, {1: 138}),          "Ca": (194, {2: 100}),
    "Sc": (184, {3: 75}),           "Ti": (176, {2: 86, 3: 67, 4: 61}),
    "V":  (171, {2: 79, 3: 64, 4: 58, 5: 54}),
    "Cr": (166, {2: 80, 3: 62, 6: 44}),
    "Mn": (161, {2: 83, 3: 65, 4: 53, 7: 46}),
    "Fe": (156, {2: 78, 3: 65}),    "Co": (152, {2: 75, 3: 61}),
    "Ni": (149, {2: 69, 3: 60}),    "Cu": (145, {1: 77, 2: 73}),
    "Zn": (142, {2: 74}),           "Ga": (136, {3: 62}),
    "Ge": (125, {4: 53}),           "As": (114, {3: 58, 5: 46}),
    "Se": (103, {2: 79, 4: 50, -2: 198}),
    "Br": (94,  {1: 196, -1: 196}), "Kr": (88,  {}),
    "Rb": (265, {1: 152}),          "Sr": (219, {2: 118}),
    "Y":  (212, {3: 90}),           "Zr": (206, {4: 72}),
    "Nb": (198, {5: 64}),           "Mo": (190, {4: 65, 6: 59}),
    "Tc": (183, {4: 65, 7: 56}),    "Ru": (178, {3: 68, 4: 62}),
    "Rh": (173, {3: 67}),           "Pd": (169, {2: 86, 4: 62}),
    "Ag": (165, {1: 115, 2: 94}),   "Cd": (161, {2: 95}),
    "In": (156, {3: 80}),           "Sn": (145, {2: 118, 4: 69}),
    "Sb": (133, {3: 76, 5: 60}),    "Te": (123, {4: 70, 6: 56, -2: 221}),
    "I":  (115, {1: 220, -1: 220, 5: 68, 7: 53}),
    "Xe": (108, {}),                "Cs": (298, {1: 167}),
    "Ba": (253, {2: 135}),          "La": (240, {3: 103}),
    "Ce": (235, {3: 102, 4: 87}),   "Pr": (239, {3: 99}),
    "Nd": (229, {3: 98}),           "Pm": (236, {3: 97}),
    "Sm": (229, {2: 127, 3: 96}),   "Eu": (233, {2: 117, 3: 95}),
    "Gd": (233, {3: 94}),           "Tb": (225, {3: 92, 4: 76}),
    "Dy": (228, {3: 91}),           "Ho": (226, {3: 90}),
    "Er": (226, {3: 89}),           "Tm": (222, {2: 103, 3: 88}),
    "Yb": (222, {2: 102, 3: 87}),   "Lu": (217, {3: 86}),
    "Hf": (208, {4: 71}),           "Ta": (200, {5: 64}),
    "W":  (193, {4: 66, 6: 60}),    "Re": (188, {4: 63, 7: 53}),
    "Os": (185, {4: 63, 8: 55}),    "Ir": (180, {3: 68, 4: 63}),
    "Pt": (177, {2: 80, 4: 63}),    "Au": (174, {1: 137, 3: 85}),
    "Hg": (171, {1: 119, 2: 102}),  "Tl": (156, {1: 150, 3: 89}),
    "Pb": (154, {2: 119, 4: 78}),   "Bi": (143, {3: 103, 5: 76}),
    "Po": (135, {2: 94, 4: 71, 6: 59}),
    "At": (127, {1: 227, -1: 227}), "Rn": (120, {}),
    "Fr": (348, {1: 180}),          "Ra": (283, {2: 148}),
    "Ac": (260, {3: 112}),          "Th": (245, {4: 94}),
    "Pa": (240, {5: 90}),           "U":  (238, {4: 89, 6: 73}),
}

RADII_INFO = """CALCULADORA DE RAIOS ATÓMICOS / IÓNICOS

Dados: Raios de Shannon (CN=6 para iões, metálico/covalente para átomos).
Valores em picómetros (pm). 1 pm = 1e-12 m = 0,01 Å.

Tendências (para estimativa quando dados em falta):
- No período: raio diminui (Z_eff aumenta)
- No grupo: raio aumenta (nova camada)
- Catião < Neutro < Anião
- Isoeletrónico: Z maior = raio menor
- Contracção lantânida: 4f blindagem fraca → 5d/6p menores que esperado

Utilização:
  1. Consultar raio conhecido (símbolo + carga opcional)
  2. Estimar desconhecido a partir de vizinhos
  3. Comparar duas espécies
"""

# ============================================================================
# FUNÇÕES AUXILIARES
# ============================================================================

def print_header(title):
    """Imprime cabeçalho formatado."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def print_subheader(title):
    """Imprime sub-cabeçalho formatado."""
    print(f"\n--- {title} ---")

def get_content(key):
    """Obtém string de conteúdo pela chave dos globals."""
    return globals().get(key, f"[Conteúdo '{key}' não definido]")

def format_content(template, vars_dict=None):
    """Formata template de conteúdo com variáveis."""
    if vars_dict is None:
        return template
    try:
        return template.format(**vars_dict)
    except KeyError as e:
        return template + f"\n[Variável em falta: {e}]"

def find_ec(query):
    """Encontra configuração electrónica por símbolo, Z, ou nome."""
    query = query.strip()
    if not query:
        return None
    if query.isdigit():
        z = int(query)
        for s, (zz, cfg) in EC.items():
            if zz == z:
                return s, zz, cfg
        return None
    # Normaliza símbolo: primeira maiúscula, resto minúscula
    s = query[0].upper() + query[1:].lower() if len(query) > 1 else query.upper()
    if s in EC:
        z, cfg = EC[s]
        return s, z, cfg
    # Busca case-insensitive
    for sym, (z, cfg) in EC.items():
        if sym.lower() == query.lower():
            return sym, z, cfg
    return None

def parse_species(text):
    """Parse de 'Fe2+', 'O-2', 'Na+'. Retorna (símbolo, carga)."""
    import re
    text = text.strip()
    if not text:
        return None, None
    m = re.match(r'([A-Z][a-z]?)([+-]?\d+)?', text)
    if not m:
        return None, None
    sym, ch = m.groups()
    charge = 0
    if ch:
        charge = int(ch)
    return sym, charge

# ============================================================================
# FUNÇÕES DE EXIBIÇÃO
# ============================================================================

def show_text_topic(content_key):
    """Exibe tópico de texto simples."""
    label = TOPICS.get(content_key, {}).get("label", content_key)
    print_header(label)
    print(get_content(content_key))

def show_config():
    """Consulta interactiva de CE."""
    print_header("Consulta de Configuração Electrónica")
    while True:
        q = input("\nSímbolo, nome, ou Z (Enter=voltar): ").strip()
        if not q:
            break
        r = find_ec(q)
        if not r:
            print(f"  Não encontrado: {q}")
            continue
        s, z, cfg = r
        print(f"\n  Z={z}  {s}  {cfg}\n")

def show_all_ec():
    """Exibe todas as 118 configurações electrónicas."""
    print_header("Todas as 118 Configurações Electrónicas")
    for s, (z, cfg) in sorted(EC.items(), key=lambda x: x[1][0]):
        print(f"  {z:3d}  {s:2s}  {cfg}")
    print()

def show_radii():
    """Calculadora interactiva de raios."""
    print_header("Calculadora de Raios Atómicos / Iónicos")
    print(RADII_INFO)
    while True:
        print("\nOpções:")
        for k, v in RADII_SUBTOPICS.items():
            print(f"  {k}. {v['label']}")
        c = input("> ").strip().lower()
        if c in ("b", "back", "q", "quit", "voltar"):
            break
        elif c == "1":
            radius_lookup()
        elif c == "2":
            radius_compare()
        elif c == "3":
            radius_estimate()
        else:
            print("  1-3 ou b")

def radius_lookup():
    """Consulta de raio único."""
    q = input("Símbolo do elemento (ex.: Fe, Fe2+, O-2): ").strip()
    if not q:
        return
    sym, charge = parse_species(q)
    if not sym or sym not in RADII_DATA:
        print(f"  Elemento desconhecido: {sym}")
        return
    arad, ions = RADII_DATA[sym]
    if charge == 0:
        print(f"  {sym} raio atómico: {arad} pm")
    elif charge in ions:
        print(f"  {sym}{charge:+d} raio iónico: {ions[charge]} pm")
    else:
        print(f"  Sem dados para {sym}{charge:+d}")
        print(f"  Cargas disponíveis: {sorted(ions.keys())}")

def radius_compare():
    """Compara duas espécies."""
    q1 = input("Primeira (ex.: Na+): ").strip()
    q2 = input("Segunda (ex.: Mg2+): ").strip()
    s1, c1 = parse_species(q1)
    s2, c2 = parse_species(q2)
    if not s1 or not s2 or s1 not in RADII_DATA or s2 not in RADII_DATA:
        print("  Inválido ou elemento desconhecido")
        return
    ar1, ions1 = RADII_DATA[s1]
    ar2, ions2 = RADII_DATA[s2]
    r1 = ar1 if c1 == 0 else ions1.get(c1)
    r2 = ar2 if c2 == 0 else ions2.get(c2)
    if r1 is None or r2 is None:
        print("  Dados em falta para uma espécie")
        return
    print(f"  {q1}: {r1} pm")
    print(f"  {q2}: {r2} pm")
    if r1 > r2:
        print(f"  {q1} é maior por {r1 - r2} pm")
    else:
        print(f"  {q2} é maior por {r2 - r1} pm")

def radius_estimate():
    """Estima por tendências periódicas."""
    q = input("Símbolo do elemento para estimar: ").strip()
    if not q:
        return
    sym = q[0].upper() + q[1:].lower() if len(q) > 1 else q.upper()
    if sym not in RADII_DATA:
        print("  Elemento desconhecido")
        return
    arad, ions = RADII_DATA[sym]
    print(f"  Raio atómico conhecido: {arad} pm")
    if ions:
        print("  Raios iónicos conhecidos:")
        for ch, rad in sorted(ions.items()):
            sign = "+" if ch > 0 else ""
            print(f"    {sym}{sign}{ch}: {rad} pm")
    # Encontra vizinhos por Z
    z = None
    for s, (zz, _) in EC.items():
        if s == sym:
            z = zz
            break
    if z:
        print("  Vizinhos:")
        for dz in (-1, 1):
            nz = z + dz
            for s, (zz, _) in EC.items():
                if zz == nz:
                    nar, _ = RADII_DATA.get(s, (None, {}))
                    if nar:
                        print(f"    {s} (Z={nz}) atómico: {nar} pm")

# ============================================================================
# MANIPULADOR DE SUBMENU
# ============================================================================

def show_submenu(parent_key):
    """Manipulador genérico de submenu."""
    submenu = SUBTOPICS.get(parent_key)
    if not submenu:
        print(f"[Submenu '{parent_key}' não definido]")
        return
    
    parent_label = TOPICS.get(parent_key, {}).get("label", parent_key)
    
    while True:
        print_header(parent_label)
        # Ordena: números primeiro, depois letras
        sorted_keys = sorted(submenu.keys(), key=lambda x: (not x.isdigit(), x))
        for k in sorted_keys:
            v = submenu[k]
            print(f"  {k}. {v['label']}")
        
        c = input("> ").strip().lower()
        if c in ("b", "back", "q", "quit", "voltar"):
            break
        
        if c not in submenu:
            print("  Opção inválida")
            continue
        
        entry = submenu[c]
        content = entry.get("content")
        
        if content == "BACK":
            break
        elif content in ("radius_lookup", "radius_compare", "radius_estimate"):
            # Funções interactivas de raios
            globals()[content]()
        elif content in SUBTOPICS:
            # Submenu aninhado
            show_submenu(content)
        elif callable(content):
            # Função callable
            content()
        else:
            # Conteúdo de texto com variáveis opcionais
            vars_dict = entry.get("vars")
            text = format_content(get_content(content), vars_dict)
            print_header(entry["label"])
            print(text)
            input("\nPrima Enter para continuar...")

# ============================================================================
# MENU PRINCIPAL
# ============================================================================

def main():
    print("Ficha de Química — TI-Nspire CX II-T")
    print("Digite 'ajuda' para comandos, 'q' para sair")
    
    while True:
        print_header("MENU PRINCIPAL")
        # Ordena: números primeiro, depois letras
        sorted_keys = sorted(TOPICS.keys(), key=lambda x: (not x.isdigit(), x))
        for k in sorted_keys:
            v = TOPICS[k]
            print(f"  {k}. {v['label']}")
        
        c = input("> ").strip().lower()
        
        if c in ("q", "quit", "exit", "sair"):
            print("Boa sorte!")
            break
        elif c in ("h", "help", "ajuda"):
            print("\nComandos: 1-11, q, ajuda")
            continue
        
        if c not in TOPICS:
            print("  Opção inválida")
            continue
        
        topic = TOPICS[c]
        ttype = topic["type"]
        content = topic["content"]
        
        if ttype == "quit":
            print("Boa sorte!")
            break
        elif ttype == "text":
            show_text_topic(content)
            input("\nPrima Enter para continuar...")
        elif ttype == "interactive":
            # Chama função pelo nome
            if content in globals():
                globals()[content]()
            else:
                print(f"[Handler '{content}' não encontrado]")
        elif ttype == "submenu":
            show_submenu(content)
        else:
            print(f"[Tipo desconhecido: {ttype}]")

# ============================================================================
# PONTO DE ENTRADA
# ============================================================================

if __name__ == "__main__":
    main()