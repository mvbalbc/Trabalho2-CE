# O "Efeito Halo" é real no jogos indie? Jogos originais de estúdios que lançaram sequências possuem um volume de "vendas acumuladas" significativamente maior do que jogos únicos de estúdios que nunca tiveram continuações?

  * A primeira pergunta (“Efeito Halo”) vira uma comparação entre dois grupos: jogos originais de estúdios/franquias que tiveram sequência versus jogos únicos de estúdios que nunca tiveram continuação. A métrica que você vai usar como “vendas acumuladas” precisa ser tratada como proxy, normalmente owners estimados.

  * A resposta estatística fica assim: você calcula a média e a mediana de owners estimados para original_com_sequencia e jogo_unico_sem_sequencia. Se os originais de franquias com sequência tiverem valores maiores, isso sugere efeito halo/spillover positivo; se não houver diferença, o efeito não aparece claramente na amostra.


# A nota média das sequências é maior, menor ou igual à dos jogos originais indie?

  * A segunda pergunta compara a nota média das sequências com a dos jogos originais indie. Aqui a análise é mais direta, porque você pode usar a coluna de avaliação/score do dataset e testar a diferença descritiva entre os grupos. Em ambos os casos, a resposta principal pode ser feita com média, mediana, quartis, desvio-padrão e gráficos de barras/boxplots.

  * Para a nota média, compare sequencia e original. Use média, mediana e boxplot, porque isso mostra não só quem tem maior nota, mas também a dispersão e os outliers. Se a sequência tiver média maior, você pode dizer que, na amostra, as continuações foram melhor avaliadas; se for menor, o oposto; se for parecida, o público avaliou de forma semelhante.

# Como fazer a análise estatística descritiva ?

  * O Kaggle deve ser sua base de catálogo e métricas estáticas: nome, gênero, tags, preço, reviews, score e owners estimados, se existirem no arquivo que você estiver usando. O SteamDB entra como apoio para confirmar sequências, verificar páginas de franquia e checar histórico quando necessário.

  * Primeiro, filtre os jogos indie. Depois, classifique os jogos em três grupos: original_com_sequencia, sequencia e jogo_unico_sem_sequencia. Para isso, você pode combinar regras automáticas de nome com validação manual, porque o dataset normalmente não traz um campo explícito de franquia.

  * Depois, calcule métricas por grupo. Para a primeira pergunta, compare owners ou outra métrica de volume entre originais com sequência e jogos únicos; para a segunda, compare o score médio entre originais e sequências. Se quiser enriquecer a análise, faça a comparação também por gênero indie.

  * A parte mais importante é documentar como você definiu “sequência” e “jogo único”. Se a regra for só automática, ela vai errar; se for híbrida, com validação manual, a qualidade aumenta bastante.

  