"""
Puerto Rico Core Statutory Corpus Seed & Ground Truth Knowledge Base.
Contains pristine official statutory texts, constitutional articles, key civil and penal provisions,
LPAU administrative rules, and leading Supreme Court D.P.R. jurisprudence precedents.
"""

from typing import List, Dict, Any

PR_CONSTITUTION_DATA = """
CONSTITUCIÓN DEL ESTADO LIBRE ASOCIADO DE PUERTO RICO (1952)

PREÁMBULO
Nosotros, el pueblo de Puerto Rico, a fin de organizarnos políticamente sobre una base plenamente democrática, promover el bienestar general y asegurar para nosotros y nuestra posteridad el goce cabal de los derechos humanos, puestos nuestra confianza en Dios Todopoderoso, ordenamos y establecemos esta Constitución para el Estado Libre Asociado que en el ejercicio de nuestro derecho natural ahora creamos.

ARTÍCULO I - DEL ESTADO LIBRE ASOCIADO
Sección 1. Se constituye el Estado Libre Asociado de Puerto Rico. Su poder político emana del pueblo y se ejercerá con arreglo a su voluntad, dentro de los términos del convenio acordado entre el pueblo de Puerto Rico y los Estados Unidos de América.
Sección 2. El gobierno del Estado Libre Asociado de Puerto Rico tendrá forma republicana y sus Poderes Legislativo, Ejecutivo y Judicial estarán igualmente subordinados a la soberanía del pueblo de Puerto Rico.

ARTÍCULO II - CARTA DE DERECHOS
Sección 1. La dignidad del ser humano es inviolable. Todos los seres humanos son iguales ante la ley. No podrá establecerse discriminación alguna por motivo de raza, color, sexo, nacimiento, origen o condición social, ni ideas políticas o religiosas. Tanto las leyes como el sistema de educación pública sustentarán estos principios de esencial igualdad humana.
Sección 2. Las leyes garantizarán la expresión de la voluntad del pueblo mediante el sufragio universal, igual, directo y secreto, y protegerán al ciudadano contra toda coacción en el ejercicio de la prerrogativa electoral.
Sección 3. No se aprobará ley alguna relativa al establecimiento de cualquier religión ni se prohibirá el libre ejercicio del culto religioso. Habrá completa separación de la iglesia y el estado.
Sección 4. No se aprobará ley alguna que restrinja la libertad de palabra o de prensa o el derecho del pueblo a reunirse en asamblea pacífica y a pedir al gobierno la reparación de agravios.
Sección 7. Se reconoce como derecho fundamental del ser humano el derecho a la vida, a la libertad y al disfrute de la propiedad. No existirá la pena de muerte. Ninguna persona será privada de su libertad o propiedad sin el debido procedimiento de ley, ni se negará a persona alguna en Puerto Rico la igual protección de las leyes.
Sección 8. Toda persona tiene derecho a protección de ley contra ataques abusivos a su honra, a su reputación y a su vida privada o familiar.
Sección 9. No se expropiará la propiedad privada a no ser para uso público y mediante el pago previo de una justa compensación fijada en la forma provista por ley.
Sección 10. No se violará el derecho del pueblo a la protección de sus personas, casas, papeles y efectos contra registros, incautaciones y allanamientos irrazonables. No se interceptará la comunicación telefónica. Sólo se expedirán mandamientos autorizando registros, allanamientos o arrestos por autoridad judicial, y únicamente cuando exista causa probable apoyada en juramento o afirmación.
Sección 11. En todos los procesos criminales, el acusado disfrutará del derecho a tener un juicio rápido y público, a ser notificado de la naturaleza y causa de la acusación recibiendo copia de la misma, a carearse con los testigos de cargo, a obtener la comparecencia compulsoria de testigos a su favor, a tener ayuda de abogado, y a presumirse inocente. En los procesos por delito grave el acusado tendrá derecho a que su juicio se ventile ante un jurado imparcial.
Sección 12. No se exigirán fianzas desproporcionadas, ni se impondrán multas excesivas ni castigos crueles e inusitados.
"""

PR_CIVIL_CODE_2020_DATA = """
CÓDIGO CIVIL DE PUERTO RICO DE 2020 (LEY NÚM. 55-2020)

TÍTULO PRELIMINAR - EFICACIA Y APLICACIÓN DE LAS LEYES
Artículo 1. Fuentes del ordenamiento jurídico. Las fuentes del ordenamiento jurídico puertorriqueño son la ley, la costumbre y los principios generales del derecho.
Artículo 2. Ignorancia de las leyes. La ignorancia de las leyes no excusa de su cumplimiento.
Artículo 7. Deber de resolver y equidad. Los tribunales no pueden abstenerse de fallar a pretexto de silencio, oscuridad o insuficiencia de la ley. La equidad se tomará en cuenta al aplicar los principios generales del derecho.

LIBRO QUINTO - OBLIGACIONES Y CONTRATOS
TÍTULO I - LAS OBLIGACIONES
Artículo 1077. Concepto de obligación. La obligación es una relación jurídica en la que un sujeto llamado deudor tiene el deber jurídico de realizar una prestación patrimonial en favor de otro sujeto llamado acreedor, quien tiene el poder correlativo de exigir su cumplimiento.
Artículo 1188. Responsabilidad por dolo y culpa contractual. Responde del incumplimiento de una obligación contractual quien actúa con dolo, culpa o mora. La responsabilidad procedente de dolo es exigible en todas las obligaciones. La renuncia a la acción para hacerla efectiva es nula.

TÍTULO II - LOS CONTRATOS EN GENERAL
Artículo 1231. Libertad de contratación. Las partes pueden establecer los pactos, cláusulas y condiciones que tengan por conveniente, siempre que no sean contrarios a la ley, a la moral ni al orden público.
Artículo 1232. Requisitos esenciales del contrato. No hay contrato sino cuando concurren los requisitos siguientes: (a) consentimiento de los contratantes; (b) objeto cierto que sea materia del contrato; y (c) causa de la obligación que se establezca.

TÍTULO IX - LA RESPONSABILIDAD CIVIL EXTRACONTRACTUAL (RESPONSABILIDAD POR CULPA O NEGLIGENCIA)
Artículo 1536. Responsabilidad por culpa o negligencia. Toda persona que por culpa o negligencia causa daño a otra viene obligada a repararlo. La culpa o negligencia consiste en la omisión de aquella diligencia que exige la naturaleza de la obligación y corresponde a las circunstancias de las personas, del tiempo y del lugar.
Artículo 1537. Concurrencia de culpas. La concurrencia de la culpa de la víctima reduce proporcionalmente el monto de la indemnización de los daños y perjuicios.
Artículo 1540. Responsabilidad por actos de terceros (Responsabilidad vicaria). La obligación de indemnizar impuesta por el Artículo 1536 es exigible no sólo por los actos u omisiones propios, sino por los de aquellas personas de quienes se debe responder: (a) los progenitores que ejercen la patria potestad responden solidariamente por los daños causados por los hijos menores que habitan con ellos; (b) los tutores responden por los daños causados por las personas sometidas a tutela que están bajo su autoridad; (c) los patronos y directores de una empresa o establecimiento responden por los daños causados por sus dependientes o empleados con motivo del desempeño de sus funciones.
Artículo 1541. Daños causados por animales. El poseedor de un animal, o el que se sirve de él, es responsable de los perjuicios que causare, aunque se le escape o extravíe, salvo que el daño provenga de fuerza mayor o de culpa de quien lo hubiese sufrido.
Artículo 1544. Prescripción de la acción extracontractual. La acción para exigir la responsabilidad civil por las obligaciones derivadas de la culpa o negligencia a que se refiere el Artículo 1536 prescribe por el transcurso de un (1) año, contado desde que lo supo el agraviado.
"""

PR_PENAL_CODE_2012_DATA = """
CÓDIGO PENAL DE PUERTO RICO DE 2012 (LEY NÚM. 146-2012)

PARTE GENERAL
Artículo 2. Principio de legalidad. No se sancionará a nadie por un hecho que la ley penal no haya previsto expresamente como delito, ni se le impondrán penas o medidas de seguridad que la ley no haya establecido previamente.
Artículo 21. Culpabilidad. Nadie puede ser sancionado penalmente por un hecho previsto en una ley penal si no lo ha realizado con dolo o negligencia.
Artículo 25. Legítima defensa. No incurre en responsabilidad penal quien actúa en defensa de su persona, de su morada, de sus derechos o de la persona o derechos de un tercero, siempre que concurran las circunstancias siguientes: (a) agresión ilegítima; (b) necesidad racional del medio empleado para impedirla o repelerla; y (c) falta de provocación suficiente por parte de quien ejerce la defensa.

PARTE ESPECIAL - DELITOS CONTRA LA PERSONA
Artículo 92. Homicidio. Toda persona que mate a otro ser humano sin premeditación, incurrirá en delito de homicidio con pena de reclusión de quince (15) años.
Artículo 93. Asesinato en primer grado. Constituye asesinato en primer grado todo asesinato perpetrado mediante veneno, acecho o tortura; o con premeditación; o en la comisión o tentativa de comisión de un delito grave como escalamiento, robo, secuestro o agresión sexual. Incurrirá en delito grave con pena fija de noventa y nueve (99) años de reclusión.
Artículo 96. Homicidio negligente. Toda persona que cause la muerte de otro ser humano por negligencia incurrirá en delito de homicidio negligente con pena de reclusión de tres (3) años. Si ocurre mientras conduce un vehículo bajo los efectos de bebidas embriagantes o sustancias controladas, será sancionada con pena de reclusión de ocho (8) años.

DELITOS CONTRA LA PROPIEDAD
Artículo 182. Apropiación ilegal agravada. Incurre en delito grave con pena de reclusión de tres (3) años quien ilegalmente se apropie de bienes muebles pertenecientes a otra persona, cuando el valor de la propiedad apropiada sea de quinientos dólares ($500) o más, o recaiga sobre fondos públicos.
Artículo 189. Robo. Toda persona que se apropie ilegalmente de bienes muebles pertenecientes a otra, sustrayéndolos de su persona o en su presencia inmediata, contra su voluntad, mediante el empleo de violencia o intimidación, incurrirá en delito grave con pena fija de quince (15) años de reclusión.
"""

PR_LPAU_DATA = """
LEY DE PROCEDIMIENTO ADMINISTRATIVO UNIFORME DEL GOBIERNO DE PUERTO RICO (LEY NÚM. 38-2017)

CAPÍTULO II - PROCEDIMIENTO DE REGLAMENTACIÓN
Sección 2.1. Notificación y publicación previa de reglamentos. La agencia publicará un aviso en un periódico de circulación general y en su sitio web notificando su intención de adoptar, enmendar o derogar un reglamento con al menos treinta (30) días de antelación para comentarios públicos.

CAPÍTULO III - PROCEDIMIENTO ADJUDICATIVO FORMAL
Sección 3.1. Oportunidad de ser oído y notificación. En toda adjudicación administrativa se garantizará el debido procedimiento de ley mediante notificación formal por escrito de las alegaciones o cargos y oportunidad razonable para contestar y presentar prueba.
Sección 3.15. Determinaciones de hechos y conclusiones de derecho. Toda resolución u orden final de una agencia contendrá determinaciones de hechos fundadas en el expediente y conclusiones de derecho debidamente fundamentadas.

CAPÍTULO IV - REVISIÓN JUDICIAL
Sección 4.2. Término y tribunal competente. Una parte afectada por una orden o resolución final de una agencia podrá presentar una solicitud de revisión judicial ante el Tribunal de Apelaciones dentro del término jurisdiccional de treinta (30) días a partir de la fecha de archivo en autos de la copia de la notificación.
"""

PR_LEADING_CASES_DATA = [
    {
        "case_name": "Pueblo v. Yip Berríos",
        "citation": "142 D.P.R. 386",
        "year": 1997,
        "area": "Derecho Procesal Penal y Prueba Pericial",
        "doctrine": "Establece los criterios de confiabilidad científica y admisibilidad de testimonio pericial en los tribunales de Puerto Rico, adoptando principios análogos a la doctrina Daubert.",
        "related_statutes": ["Código Penal de 2012 Art. 21", "Reglas de Evidencia de Puerto Rico Regla 702"]
    },
    {
        "case_name": "Ramos v. Argos",
        "citation": "143 D.P.R. 887",
        "year": 1997,
        "area": "Responsabilidad Civil Extracontractual",
        "doctrine": "Reitera los tres elementos constitutivos cardinales de la causa de acción por culpa o negligencia: (1) daño real demostrado, (2) acto u omisión culposa o negligente, y (3) nexo de causalidad adecuada entre la conducta y el daño resultante.",
        "related_statutes": ["Código Civil 2020 Art. 1536", "31 LPRA § 5141 (Histórico)"]
    },
    {
        "case_name": "López v. Porrata Doria",
        "citation": "169 D.P.R. 320",
        "year": 2006,
        "area": "Responsabilidad Vicaria y Anfitriones Sociales",
        "doctrine": "Doctrina del anfitrión social y patrono: Quien provee bebidas alcohólicas a una persona en estado de embriaguez evidente cuando sabe que dicha persona conducirá un vehículo de motor puede responder civilmente por los daños causados a terceros.",
        "related_statutes": ["Código Civil 2020 Art. 1540", "31 LPRA § 5142 (Histórico)"]
    },
    {
        "case_name": "Cotto v. C.M. Ins. Co.",
        "citation": "116 D.P.R. 644",
        "year": 1985,
        "area": "Prescripción Extracontractual",
        "doctrine": "El término prescriptivo de un año para ejercitar una acción de daños comienza a decursar cuando el perjudicado tiene conocimiento objetivo tanto del daño sufrido como de la persona o entidad causante del mismo.",
        "related_statutes": ["Código Civil 2020 Art. 1544", "31 LPRA § 5298 (Histórico)"]
    },
    {
        "case_name": "San Gerónimo Caribe Project v. ELA",
        "citation": "174 D.P.R. 640",
        "year": 2008,
        "area": "Dominio Público y Zona Marítimo-Terrestre",
        "doctrine": "Establece la imprescriptibilidad, inalienabilidad e inembargabilidad de los bienes de dominio público marítimo-terrestre en Puerto Rico bajo el Artículo 8 de la Ley de Aguas y la Constitución.",
        "related_statutes": ["Const. PR Art. II, Sec. 9", "Código Civil 2020 Bienes de Dominio Público"]
    }
]

def get_all_pr_statutory_sources() -> List[Dict[str, Any]]:
    """Returns all curated primary statutory sources with metadata for AST parsing."""
    return [
        {
            "name": "Constitución de Puerto Rico",
            "text": PR_CONSTITUTION_DATA,
            "metadata": {
                "source_origin": "Convención Constituyente / Rama Judicial",
                "source_url": "https://www.ramajudicial.pr/leyes/constitucion-pr.htm",
                "effective_date": "1952-07-25",
                "category": "Constitucional"
            }
        },
        {
            "name": "Código Civil de Puerto Rico de 2020",
            "text": PR_CIVIL_CODE_2020_DATA,
            "metadata": {
                "source_origin": "Asamblea Legislativa de Puerto Rico (Ley Núm. 55-2020)",
                "source_url": "https://sutra.oslpr.org/osl/leyes/2020/ley-055-2020.pdf",
                "effective_date": "2020-11-28",
                "category": "Derecho Civil"
            }
        },
        {
            "name": "Código Penal de Puerto Rico de 2012",
            "text": PR_PENAL_CODE_2012_DATA,
            "metadata": {
                "source_origin": "Asamblea Legislativa de Puerto Rico (Ley Núm. 146-2012)",
                "source_url": "https://sutra.oslpr.org/osl/leyes/2012/ley-146-2012.pdf",
                "effective_date": "2012-09-01",
                "category": "Derecho Penal"
            }
        },
        {
            "name": "Ley de Procedimiento Administrativo Uniforme (LPAU)",
            "text": PR_LPAU_DATA,
            "metadata": {
                "source_origin": "Asamblea Legislativa de Puerto Rico (Ley Núm. 38-2017)",
                "source_url": "https://sutra.oslpr.org/osl/leyes/2017/ley-038-2017.pdf",
                "effective_date": "2017-06-30",
                "category": "Derecho Administrativo"
            }
        }
    ]
