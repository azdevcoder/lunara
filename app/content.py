"""Conteúdo editorial e listas de opções do Lunara."""
from datetime import date, timedelta

# Ícones profissionais - mapeamento para o sistema _icons.html
# Estes ícones substituem os emojis para uma aparência mais profissional

SYMPTOMS = [
    ("cramps", "Cólicas", "icon-cramps"),
    ("headache", "Dor de cabeça", "icon-headache"),
    ("backache", "Dor lombar", "icon-backache"),
    ("bloating", "Inchaço", "icon-bloating"),
    ("acne", "Acne", "icon-acne"),
    ("tender_breasts", "Seios sensíveis", "icon-breasts"),
    ("nausea", "Náusea", "icon-nausea"),
    ("fatigue", "Cansaço", "icon-fatigue"),
    ("insomnia", "Insônia", "icon-insomnia"),
    ("diarrhea", "Intestino solto", "icon-diarrhea"),
    ("constipation", "Intestino preso", "icon-constipation"),
    ("cravings", "Desejo por doces", "icon-cravings"),
    ("dizziness", "Tontura", "icon-dizziness"),
    ("anxiety", "Ansiedade", "icon-anxiety"),
]

SYMPTOMS_MAP = {key: (label, emoji) for key, label, emoji in SYMPTOMS}

MOODS = [
    ("happy", "Feliz", "icon-happy"),
    ("calm", "Calma", "icon-calm"),
    ("sensitive", "Sensível", "icon-sensitive"),
    ("irritated", "Irritada", "icon-irritated"),
    ("anxious", "Ansiosa", "icon-anxious"),
    ("low", "Para baixo", "icon-low"),
    ("energetic", "Disposta", "icon-energetic"),
    ("tired", "Cansada", "icon-tired"),
]

MOODS_MAP = {key: (label, emoji) for key, label, emoji in MOODS}

FLOW_OPTIONS = [
    ("none", "Sem fluxo", "icon-none"),
    ("spotting", "Escape", "icon-spotting"),
    ("light", "Leve", "icon-light"),
    ("medium", "Médio", "icon-medium"),
    ("heavy", "Intenso", "icon-heavy"),
]

SEX_OPTIONS = [
    ("", "Prefiro não dizer"),
    ("protected", "Com proteção"),
    ("unprotected", "Sem proteção"),
    ("solo", "Sozinha"),
    ("oral", "Sexo oral"),
]

DISCHARGE_OPTIONS = [
    ("", "Não observei"),
    ("none", "Nenhuma"),
    ("creamy", "Cremosa"),
    ("watery", "Aquosa"),
    ("eggwhite", "Clara de ovo"),
    ("sticky", "Pegajosa"),
    ("unusual", "Diferente do normal"),
]

GOALS = [
    ("ciclo", "Entender meu ciclo", "icon-cycle", "Fases, previsões e sintomas"),
    ("engravidar", "Quero engravidar", "icon-getting-pregnant", "Janela fértil e ovulação"),
    ("gestacao", "Estou grávida", "icon-pregnancy", "Semanas e evolução do bebê"),
    ("contracepcao", "Evitar gravidez", "icon-contraception", "Lembretes e método"),
    ("menopausa", "Perimenopausa", "icon-menopause", "Calor, humor e sono"),
]

DAILY_INSIGHTS = {
    "menstrual": [
        ("Diminua o ritmo", "Seu corpo está trabalhando. Troque o treino intenso por uma caminhada e capriche no ferro: feijão, lentilha e folhas escuras ajudam."),
        ("Calor que acalma", "Uma bolsa térmica na lombar ou no abdômen por 20 minutos pode aliviar cólicas. Respire fundo e permita-se descansar."),
        ("Hidratação importa", "Mesmo sem sede, beba água ao longo do dia. Isso reduz inchaço e dor de cabeça."),
        ("Seu fluxo, sua normalidade", "Fluxos variam de mês para mês. O importante é observar mudanças muito bruscas ou sangramento que fuja do seu padrão."),
        ("Gentileza consigo", "Se a energia está baixa, faça menos e sem culpa. Seu ciclo não pede produtividade constante."),
    ],
    "follicular": [
        ("Energia em ascensão", "O estrogênio está subindo. Aproveite para treinos de força, projetos novos e encontros sociais."),
        ("Foco e clareza", "Muitas pessoas relatam mais concentração nesta fase. Reserve um bloco para aquela tarefa que vem sendo adiada."),
        ("Fibra e cor", "Frutas, legumes e grãos integrais ajudam o corpo a metabolizar o estrogênio e sustentam a energia."),
        ("Observe a secreção", "A textura muda ao longo do ciclo. Registrar ajuda a reconhecer seu padrão fértil."),
        ("Planeje com carinho", "É uma boa fase para marcar consultas, exames de rotina e revisar seus objetivos de saúde."),
    ],
    "ovulatory": [
        ("Pico de energia", "A ovulação costuma trazer disposição e sociabilidade. Aproveite, mas respeite seus limites."),
        ("Janela fértil", "Se deseja engravidar, relações nos dias férteis aumentam as chances. Se não deseja, use proteção."),
        ("Libido pode aumentar", "É comum sentir mais vontade de se relacionar. Sem julgamento: observe e registre se quiser."),
        ("Atente ao corpo", "Algumas pessoas sentem dor leve em um lado do baixo ventre. Se for intensa ou recorrente, converse com um profissional."),
        ("Hidrate e alongue", "Movimentos suaves e boa hidratação ajudam a manter o bem-estar no pico hormonal."),
    ],
    "luteal": [
        ("TPM não é frescura", "A queda de progesterona pode afetar humor, sono e apetite. Nomear o que sente já ajuda."),
        ("Estabilize o açúcar no sangue", "Refeições com proteína, fibra e gordura boa podem reduzir picos de fome e irritabilidade."),
        ("Sono é prioridade", "Tente deitar no mesmo horário e reduzir telas antes de dormir. O descanso ameniza os sintomas."),
        ("Menos sal, menos inchaço", "Diminuir ultraprocessados e beber água costuma ajudar na retenção de líquidos."),
        ("Autocompaixão", "Se a irritação aparecer, avise quem está perto e reserve pausas. Você não precisa dar conta de tudo hoje."),
    ],
    "unknown": [
        ("Comece pelo primeiro dia", "Registre o início do seu período para o Lunara começar a desenhar suas previsões."),
        ("Pequenos registros, grandes padrões", "Anotar sono, humor e sintomas por algumas semanas revela conexões que passam despercebidas."),
        ("Sem pressa", "As primeiras previsões são estimativas. Elas ficam mais precisas conforme você registra."),
        ("Privacidade primeiro", "Seus dados ficam no seu próprio banco MySQL. Você pode exportar ou apagar tudo quando quiser."),
    ],
}

ARTICLES = [
    {
        "slug": "entendendo-seu-ciclo",
        "title": "Entendendo seu ciclo menstrual",
        "category": "Ciclo",
        "emoji": "icon-cycle",
        "read_time": "6 min",
        "excerpt": "As quatro fases do ciclo, o que acontece em cada uma e por que a duração varia tanto de pessoa para pessoa.",
        "body": """
            <p>O ciclo menstrual não é só a menstruação. Ele começa no primeiro dia de sangramento e vai até o dia anterior ao próximo período. Um ciclo típico dura entre 21 e 35 dias, mas a média de 28 não é uma regra — é apenas uma referência.</p>
            <h2>Fase menstrual</h2>
            <p>O útero elimina o endométrio, camada que se preparou para uma possível gestação. Pode durar de 2 a 7 dias. Cólicas, cansaço e dor lombar são comuns, mas não deveriam impedir sua rotina. Se a dor for incapacitante, vale investigar.</p>
            <h2>Fase folicular</h2>
            <p>O estrogênio sobe e os folículos ovarianos começam a amadurecer. É quando muitas pessoas se sentem mais dispostas, com humor estável e energia para começar coisas novas.</p>
            <h2>Ovulação</h2>
            <p>Um óvulo é liberado, geralmente no meio do ciclo. A janela fértil vai de cerca de cinco dias antes até um dia depois da ovulação, porque espermatozoides sobrevivem alguns dias e o óvulo, cerca de 24 horas.</p>
            <h2>Fase lútea</h2>
            <p>O corpo produz progesterona para sustentar uma possível gestação. Se ela não acontece, os níveis caem e surgem os sintomas de TPM: irritabilidade, seios sensíveis, vontade de doces, inchaço e sono.</p>
            <p class="article-note">O Lunara calcula suas fases a partir dos registros reais. Quanto mais dias você anota, mais próximas da sua realidade ficam as previsões.</p>
        """,
    },
    {
        "slug": "janela-fertil",
        "title": "O que é a janela fértil?",
        "category": "Fertilidade",
        "emoji": "icon-getting-pregnant",
        "read_time": "5 min",
        "excerpt": "Entenda os dias com maior chance de gravidez e como o app estima esse período.",
        "body": """
            <p>A janela fértil é o conjunto de dias em que a chance de gravidez é maior. Ela existe porque o espermatozoide pode sobreviver até cinco dias no trato reprodutivo, enquanto o óvulo vive cerca de 24 horas após a ovulação.</p>
            <h2>Como o cálculo é feito</h2>
            <p>O Lunara parte da data prevista para a próxima menstruação e recua 14 dias para estimar a ovulação. A janela fértil vai de cinco dias antes até um dia depois. Se seus ciclos são irregulares, essa estimativa é menos precisa — e tudo bem: ela é um mapa, não uma garantia.</p>
            <h2>Sinais que podem ajudar</h2>
            <ul>
                <li>Muco cervical transparente, elástico, parecido com clara de ovo.</li>
                <li>Leve dor em um lado do baixo ventre.</li>
                <li>Aumento da libido.</li>
                <li>Temperatura basal levemente mais alta após a ovulação.</li>
            </ul>
            <h2>Para quem quer engravidar</h2>
            <p>Relações a cada um ou dois dias durante a janela fértil costumam ser suficientes. Não é necessário testar todos os dias nem transformar a intimidade em obrigação.</p>
            <h2>Para quem quer evitar</h2>
            <p>O método do calendário não é confiável como contracepção, especialmente com ciclos irregulares. Use preservativo ou converse com um profissional sobre métodos mais eficazes.</p>
        """,
    },
    {
        "slug": "tpm-por-que-voce-sente-tudo",
        "title": "TPM: por que você sente tudo isso?",
        "category": "Bem-estar",
        "emoji": "alert",
        "read_time": "7 min",
        "excerpt": "Humor, sono, apetite e corpo mudam na fase lútea. Veja o que ajuda de verdade.",
        "body": """
            <p>A tensão pré-menstrual é real e envolve mudanças hormonais, neurotransmissores e fatores de estilo de vida. Os sintomas costumam aparecer de 5 a 10 dias antes da menstruação e melhorar quando o fluxo começa.</p>
            <h2>O que pode piorar</h2>
            <p>Privação de sono, estresse crônico, álcool, cafeína em excesso e dietas muito restritivas podem intensificar irritabilidade, ansiedade e vontade de doces.</p>
            <h2>O que costuma ajudar</h2>
            <ul>
                <li>Refeições regulares com proteína, fibras e gorduras boas.</li>
                <li>Movimento leve: caminhada, yoga, alongamento.</li>
                <li>Reduzir sal e ultraprocessados nos dias de inchaço.</li>
                <li>Magnésio e vitamina B6 podem ajudar em alguns casos — converse antes de suplementar.</li>
                <li>Registrar sintomas para reconhecer padrões e se preparar.</li>
            </ul>
            <h2>Quando buscar ajuda</h2>
            <p>Se os sintomas atrapalham trabalho, relações ou autocuidado todos os meses, pode ser TDPM (transtorno disfórico pré-menstrual). Não é falta de força de vontade: é uma condição reconhecida e tratável.</p>
        """,
    },
    {
        "slug": "fluxo-o-que-e-normal",
        "title": "Fluxo menstrual: o que é normal?",
        "category": "Ciclo",
        "emoji": "droplet",
        "read_time": "4 min",
        "excerpt": "Cores, coágulos, volume e duração: como diferenciar variação de alerta.",
        "body": """
            <p>Não existe um fluxo universalmente normal. A média fica entre 30 e 80 ml por ciclo, mas medir isso em colheres não é prático. Observe duração, necessidade de troca e impacto na rotina.</p>
            <h2>Variações comuns</h2>
            <p>O sangue pode ser vermelho-vivo, marrom ou mais escuro no início e no fim. Pequenos coágulos, especialmente nos dias mais intensos, costumam ser normais.</p>
            <h2>Vale investigar</h2>
            <ul>
                <li>Trocar absorvente ou coletor a cada hora por várias horas.</li>
                <li>Sangramento que dura mais de 7 dias.</li>
                <li>Coágulos maiores que uma moeda de 2 reais com frequência.</li>
                <li>Sangramento entre períodos ou após relações.</li>
                <li>Cólicas que não melhoram com analgésico comum.</li>
                <li>Ciclos menores que 21 ou maiores que 35 dias de forma persistente.</li>
            </ul>
            <p class="article-note">Estas informações não substituem uma avaliação médica. Se algo mudou de forma persistente no seu corpo, procure um profissional.</p>
        """,
    },
    {
        "slug": "sono-e-ciclo",
        "title": "Sono e ciclo: a conexão",
        "category": "Bem-estar",
        "emoji": "sleep",
        "read_time": "5 min",
        "excerpt": "Por que o sono muda ao longo do mês e como criar uma rotina que respeite suas fases.",
        "body": """
            <p>A temperatura corporal e a progesterona mudam ao longo do ciclo, e isso influencia a qualidade do sono. Na fase lútea, muitas pessoas demoram mais para pegar no sono e acordam durante a noite.</p>
            <h2>Uma rotina possível</h2>
            <ul>
                <li>Horário consistente para dormir e acordar, inclusive nos fins de semana.</li>
                <li>Luz baixa e telas longe da cama na última hora.</li>
                <li>Quarto fresco e escuro.</li>
                <li>Cafeína até o início da tarde, especialmente na TPM.</li>
                <li>Registrar horas de sono no app para enxergar seu padrão.</li>
            </ul>
            <p>Se a insônia for intensa por várias semanas ou vier acompanhada de ansiedade significativa, converse com um profissional de saúde.</p>
        """,
    },
    {
        "slug": "metodos-contraceptivos",
        "title": "Métodos contraceptivos: o básico",
        "category": "Contracepção",
        "emoji": "icon-contraception",
        "read_time": "8 min",
        "excerpt": "Preservativo, pílula, DIU, implante e mais: como conversar sobre o assunto sem tabu.",
        "body": """
            <p>Existem muitos métodos, com eficácias e efeitos diferentes. A escolha depende de saúde, rotina, planos reprodutivos e preferência pessoal. O primeiro passo é uma consulta com profissional de saúde.</p>
            <h2>Métodos de barreira</h2>
            <p>Preservativo interno e externo protegem de infecções sexualmente transmissíveis e têm eficácia boa quando usados corretamente. São o único método que também previne ISTs.</p>
            <h2>Métodos hormonais</h2>
            <p>Pílula, adesivo, anel, injetável, implante e DIU hormonal atuam de formas diferentes. Podem reduzir cólicas e regular o fluxo, mas têm contraindicações e efeitos possíveis.</p>
            <h2>DIU de cobre</h2>
            <p>Não hormonal, dura vários anos e é muito eficaz. Pode aumentar fluxo e cólicas nos primeiros meses.</p>
            <h2>Lembrete importante</h2>
            <p>Nenhum método, exceto a abstinência, é 100% eficaz. O aplicativo pode lembrar você de tomar a pílula, mas não substitui orientação profissional.</p>
        """,
    },
    {
        "slug": "primeiras-semanas-de-gestacao",
        "title": "Primeiras semanas de gestação",
        "category": "Gestação",
        "emoji": "icon-pregnancy",
        "read_time": "6 min",
        "excerpt": "O que acontece no início, quais sintomas são comuns e quando procurar ajuda.",
        "body": """
            <p>Nas primeiras semanas, o embrião se implanta no útero e começa a produzir hCG, hormônio detectado nos testes de gravidez. Muitas pessoas só descobrem depois de um atraso menstrual.</p>
            <h2>Sintomas comuns</h2>
            <ul>
                <li>Seios sensíveis einchados.</li>
                <li>Cansaço intenso.</li>
                <li>Náuseas, às vezes sem vômito.</li>
                <li>Vontade frequente de urinar.</li>
                <li>Aversões alimentares e sonolência.</li>
            </ul>
            <h2>Primeiros passos</h2>
            <p>Agende uma consulta pré-natal, inicie ácido fólico conforme orientação e evite álcool e tabaco. Não é necessário mudar tudo de uma vez: vá com calma.</p>
            <h2>Quando procurar ajuda</h2>
            <p>Sangramento intenso, dor forte em um lado, febre, vômitos persistentes ou desmaio exigem avaliação imediata.</p>
            <p class="article-note">O modo gestação do Lunara estima semanas e datas com base na DUM ou na data provável do parto. Confirme sempre com seu pré-natal.</p>
        """,
    },
    {
        "slug": "alimentacao-e-ciclo",
        "title": "Alimentação e ciclo: o que faz diferença",
        "category": "Bem-estar",
        "emoji": "salad",
        "read_time": "6 min",
        "excerpt": "Sem dietas milagrosas: ajustes simples para energia, humor e cólicas.",
        "body": """
            <p>Não existe alimento que elimine a TPM, mas a forma como você come ao longo do mês influencia energia, inchaço e fome.</p>
            <h2>Na fase menstrual</h2>
            <p>Ferro é importante: feijão, lentilha, grão-de-bico, carnes magras e folhas escuras. Combine com vitamina C (laranja, acerola, pimentão) para melhorar a absorção.</p>
            <h2>Na fase folicular</h2>
            <p>Aproveite para variar cores no prato. Vegetais crucíferos, frutas e grãos integrais apoiam o metabolismo hormonal.</p>
            <h2>Na fase lútea</h2>
            <p>Estabilidade glicêmica ajuda: proteína no café da manhã, lanches com castanhas e iogurte, menos ultraprocessados. Magnésio (sementes, cacau, folhas verdes) pode ajudar com desejo por chocolate — e um pouco de chocolate amargo também cabe.</p>
            <p class="article-note">Necessidades individuais variam. Em caso de condições de saúde ou gestação, siga a orientação de nutricionista ou médico.</p>
        """,
    },
    {
        "slug": "quando-procurar-um-profissional",
        "title": "Quando procurar um profissional",
        "category": "Saúde",
        "emoji": "stethoscope",
        "read_time": "4 min",
        "excerpt": "Sinais que merecem atenção e como se preparar para a consulta.",
        "body": """
            <p>Acompanhar o ciclo ajuda a perceber o que é padrão para você. Alguns sinais, porém, pedem avaliação profissional.</p>
            <h2>Sinais de alerta</h2>
            <ul>
                <li>Dor pélvica intensa que não melhora com analgésico.</li>
                <li>Sangramento abundante, com coágulos grandes ou por mais de 7 dias.</li>
                <li>Sangramento entre períodos ou após relações.</li>
                <li>Atrasos repetidos sem gravidez, ou ciclos muito irregulares.</li>
                <li>Corrimento com odor forte, coceira ou dor.</li>
                <li>Fogachos intensos, secura vaginal ou mudanças bruscas na libido.</li>
            </ul>
            <h2>Como se preparar</h2>
            <p>Leve suas datas, sintomas e medicamentos. O Lunara permite exportar seus registros em CSV ou JSON — você pode compartilhar o que fizer sentido com quem vai te atender.</p>
            <p class="article-note">Este app é uma ferramenta de autoconhecimento, não um diagnóstico. Em emergências, procure atendimento imediatamente.</p>
        """,
    },
]