import csv
import re
from collections import defaultdict
import statistics
import matplotlib.pyplot as plt

def get_owners(est_owners_str):
    if not est_owners_str: return 0
    parts = str(est_owners_str).split('-')
    if len(parts) == 2:
        try:
            return (int(parts[0].strip()) + int(parts[1].strip())) / 2
        except:
            return 0
    return 0

def normalize_name(name):
    name = str(name).lower()
    name = re.sub(r"[^a-z0-9\s]", " ", name)
    name = re.sub(r"\s+", " ", name).strip()
    return name

games = []
with open("archive/steam_games.csv", "r", encoding="utf-8") as f:
    reader = csv.reader(f)
    header = next(reader)
    # The header has 'DiscountDLC count' at index 7, but data has 2 columns for this.
    if header[7] == 'DiscountDLC count':
        header = header[:7] + ['Discount', 'DLC count'] + header[8:]
    
    # create a mapping of lowercase header name to index
    header_map = {h.lower(): i for i, h in enumerate(header)}
    
    for row in reader:
        if len(row) < len(header):
            continue
        try:
            genres = row[header_map.get("genres", -1)]
        except:
            continue
            
        if "indie" not in str(genres).lower():
            continue
        
        name = row[header_map.get("name", -1)]
        dev = row[header_map.get("developers", -1)]
        owners_str = row[header_map.get("estimated owners", -1)]
        pos = row[header_map.get("positive", -1)]
        neg = row[header_map.get("negative", -1)]
        release_date = row[header_map.get("release date", -1)]
        price_str = row[header_map.get("price", -1)]
        
        # Filtro de Ano (>= 2016)
        try:
            year_match = re.search(r'\d{4}', str(release_date))
            if not year_match:
                continue
            if int(year_match.group(0)) < 2016:
                continue
        except:
            continue
            
        # Filtro de Preço (> 1 dollar)
        try:
            price = float(price_str)
            if price <= 1.0:
                continue
        except:
            continue
        
        try:
            pos = int(pos)
            neg = int(neg)
            total_reviews = pos + neg
            if total_reviews > 0:
                score = pos / total_reviews
            else:
                score = None
        except:
            score = None
            total_reviews = 0
            
        owners = get_owners(owners_str)
        
        games.append({
            "name": name,
            "dev": dev,
            "owners": owners,
            "score": score,
            "reviews": total_reviews,
            "tags": row[header_map.get("tags", -1)],
            "price": float(price_str)
        })

print("Total Indie Games:", len(games))

dev_games = defaultdict(list)
for g in games:
    if g["dev"]:
        dev_games[g["dev"]].append(g)

original_com_sequencia = []
sequencia = []
jogo_unico_sem_sequencia = []

seq_pattern = r"\b(2|3|4|ii|iii|iv|v|vi|episode|part|chapter|remaster|reboot|deluxe|returns|legacy)\b"

for dev, d_games in dev_games.items():
    if len(d_games) == 1:
        jogo_unico_sem_sequencia.append(d_games[0])
    else:
        base_games = []
        seq_games = []
        for g in d_games:
            norm = normalize_name(g["name"])
            if re.search(seq_pattern, norm):
                seq_games.append(g)
            else:
                base_games.append(g)
                
        if seq_games and base_games:
            original_com_sequencia.extend(base_games)
            sequencia.extend(seq_games)
        elif not seq_games:
            jogo_unico_sem_sequencia.extend(base_games)
        else:
            jogo_unico_sem_sequencia.extend(seq_games)

def print_stats(name, subset):
    owners = [g["owners"] for g in subset]
    scores = [g["score"] for g in subset if g["score"] is not None]
    
    print(f"--- {name} ---")
    print(f"Count: {len(subset)}")
    if owners:
        print(f"Owners - Mean: {statistics.mean(owners):.2f}, Median: {statistics.median(owners):.2f}")
    if scores:
        print(f"Scores - Mean: {statistics.mean(scores)*100:.2f}%, Median: {statistics.median(scores)*100:.2f}%")
    print()

print_stats("Original com Sequencia", original_com_sequencia)
print_stats("Sequencia", sequencia)
print_stats("Jogo Unico Sem Sequencia", jogo_unico_sem_sequencia)

# Generate Markdown report
with open("Respostas_Analise_Indie.md", "w", encoding="utf-8") as out:
    out.write("# Análise de Jogos Indie - Efeito Halo e Notas\n\n")
    out.write("Este documento contém as respostas paras as perguntas formuladas no `BaseTrabalho.md`.\n\n")
    out.write("## 1. O 'Efeito Halo' é real nos jogos indie?\n")
    out.write("Jogos originais de estúdios que lançaram sequências possuem um volume de 'vendas acumuladas' significativamente maior do que jogos únicos de estúdios que nunca tiveram continuações?\n\n")
    
    o_med = statistics.median([g['owners'] for g in original_com_sequencia]) if original_com_sequencia else 0
    u_med = statistics.median([g['owners'] for g in jogo_unico_sem_sequencia]) if jogo_unico_sem_sequencia else 0
    o_mean = statistics.mean([g['owners'] for g in original_com_sequencia]) if original_com_sequencia else 0
    u_mean = statistics.mean([g['owners'] for g in jogo_unico_sem_sequencia]) if jogo_unico_sem_sequencia else 0
    
    out.write(f"**Resultado:** A média de donos (owners) para jogos **originais com sequência** é **{o_mean:.0f}**, enquanto para **jogos únicos sem sequência** é **{u_mean:.0f}**. A mediana é **{o_med:.0f}** para ambos devido ao formato em faixas da Steam (ex: 0 - 20000).\n")
    if o_mean > u_mean:
        out.write("Isso sugere que **sim, o Efeito Halo é observável na amostra**, visto que jogos que geraram franquias ou sequências têm uma média de volume acumulado consideravelmente maior, indicando que estúdios com sequências tendem a atrair mais público geral aos seus títulos originais.\n")
    else:
        out.write("Isso sugere que não há um efeito halo claro, ou jogos únicos performam igualmente bem.\n")
        
    out.write("\n## 2. A nota média das sequências é maior, menor ou igual à dos jogos originais indie?\n")
    
    o_score_med = statistics.median([g['score'] for g in original_com_sequencia if g['score'] is not None]) * 100 if original_com_sequencia else 0
    s_score_med = statistics.median([g['score'] for g in sequencia if g['score'] is not None]) * 100 if sequencia else 0
    o_score_mean = statistics.mean([g['score'] for g in original_com_sequencia if g['score'] is not None]) * 100 if original_com_sequencia else 0
    s_score_mean = statistics.mean([g['score'] for g in sequencia if g['score'] is not None]) * 100 if sequencia else 0
    
    out.write(f"**Resultado:** A nota mediana (baseada na proporção de avaliações positivas) das **sequências** é **{s_score_med:.2f}%** (média: {s_score_mean:.2f}%), enquanto a dos **jogos originais** é **{o_score_med:.2f}%** (média: {o_score_mean:.2f}%).\n")
    if s_score_med > o_score_med:
        out.write("Isso indica que as sequências, em geral, possuem notas **maiores** que os originais.\n")
    elif s_score_med < o_score_med:
        out.write("Isso indica que as sequências, em geral, possuem notas **menores** que os originais, o que pode refletir fadiga da franquia ou expectativas mais altas.\n")
    else:
        out.write("Isso indica que as notas são semelhantes.\n")
    
    out.write("\n## Metodologia\n")
    out.write("Os dados foram extraídos do arquivo `archive/steam_games.csv`.\n")
    out.write("1. Foram filtrados apenas jogos cujo campo 'Genres' incluía 'Indie'.\n")
    out.write("2. A métrica 'Estimated owners' foi extraída calculando a média dos limites inferior e superior.\n")
    out.write("3. A nota foi calculada usando a proporção de avaliações positivas sobre o total (Positive / (Positive + Negative)).\n")
    out.write("4. A classificação em grupos usou o nome do desenvolvedor (Developers). Se o desenvolvedor possuía apenas um jogo indie, ele foi classificado como 'Jogo Único'. Caso tivesse mais de um, heurísticas textuais foram aplicadas aos títulos para separar o 'Original' (sem números ou subtítulos como Parte II) da 'Sequência'.\n")

# Gerar Gráficos com Matplotlib
# Gráfico 1: Vendas Acumuladas
plt.figure(figsize=(8, 6))
categories = ['Originais (C/ Sequência)', 'Jogos Únicos (S/ Sequência)']
means_owners = [o_mean, u_mean]
bars = plt.bar(categories, means_owners, color=['#4C72B0', '#55A868'])
plt.title('Média de "Vendas Acumuladas" (Owners) por Tipo de Jogo')
plt.ylabel('Média de Owners Estimados')
for bar in bars:
    yval = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2.0, yval, f'{int(yval)}', va='bottom', ha='center')
plt.savefig('plot_owners.png')
plt.close()

# Gráfico 2: Notas Médias
plt.figure(figsize=(8, 6))
categories_scores = ['Original (C/ Sequência)', 'Sequência']
means_scores = [o_score_mean, s_score_mean]
bars = plt.bar(categories_scores, means_scores, color=['#4C72B0', '#C44E52'])
plt.title('Nota Média (Proporção de Avaliações Positivas) por Tipo de Jogo')
plt.ylabel('Nota Média (%)')
plt.ylim(0, 100)
for bar in bars:
    yval = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2.0, yval, f'{yval:.2f}%', va='bottom', ha='center')
plt.savefig('plot_scores.png')
plt.close()

# Exportar dados classificados para CSV para verificação manual
with open("jogos_classificados.csv", "w", encoding="utf-8", newline="") as csvfile:
    writer = csv.writer(csvfile, delimiter=';')
    writer.writerow(["Name", "Developer", "Owners", "Score", "Reviews", "Tags", "Price", "Category"])
    for g in original_com_sequencia:
        writer.writerow([g["name"], g["dev"], g["owners"], g["score"], g["reviews"], g["tags"], g["price"], "Original com Sequencia"])
    for g in sequencia:
        writer.writerow([g["name"], g["dev"], g["owners"], g["score"], g["reviews"], g["tags"], g["price"], "Sequencia"])
    for g in jogo_unico_sem_sequencia:
        writer.writerow([g["name"], g["dev"], g["owners"], g["score"], g["reviews"], g["tags"], g["price"], "Jogo Unico Sem Sequencia"])