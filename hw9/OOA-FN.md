# 基因演算法 OOA：操作與協作規格

對應 [OOA-EN.MMD](./OOA-EN.MMD)，以 [原始題目](./readme2.md) 為依據。圖中的 `OptimizationProblem` 是明確的行為契約，兩個情境都實作相同操作；`Individual` 持有染色體，不是 `ProductionSchedule` 或 `RecommendationList` 的父類別。以下是可供實作的分析模型，未指定設計模式。

## 共同資料與約定

- `Individual` 是候選解；`Chromosome` 是有序基因集合。排程基因的值為 `ProductionTask`；推薦基因的值為 `Product`，同一商品可以重複出現，代表購買多件。`Gene.value` 的具體型別安全表示方式留給設計階段。
- `Fitness` 包含是否可行與分數；比較時可行解優先，再比較分數（越大越好）。不可行解不得作為最終結果；若最終種群沒有可行解，回報無可行解。評估始終依目前染色體進行，不能沿用變更前的分數。
- 下述評分、篩選、交配與變異是**分析時選擇的可實作範例**，不是題目指定的唯一公式。演算法具隨機性，不保證最佳解。
- 種群大小至少為 2、迭代上限為非負數。`solve` 接受情境、種群大小及上限；隨機來源、交配率、變異率和終止條件可由實作設定。圖中 `crossover` 每次回傳一個後代；需要第二個時可再呼叫一次。

## 共用演算法

### FN-01 `GeneticAlgorithm.solve(problem, populationSize, maxIterations)`
- **主要行為**：驗證輸入，建立初始種群；每代依序篩選、交配、變異並替換種群，最後回傳最終種群最佳可行個體。
- **觸發時機**：應用程式要求解某個最佳化問題時。
- **被誰觸發**：排程或推薦情境的呼叫端。
- **協作對象**：`OptimizationProblem`、`Population`、`Individual`。
- **會觸發誰**：依序呼叫 FN-02；各代呼叫 FN-03、FN-04、FN-05；到達迭代上限或終止條件後呼叫 FN-06。上限為零時直接評估初始種群。

### FN-02 `GeneticAlgorithm.initializePopulation(problem, populationSize)`
- **主要行為**：建立指定數量的初始個體並組成種群。
- **觸發時機**：開始演化前。
- **被誰觸發**：FN-01。
- **協作對象**：`OptimizationProblem`、`Population`、`Individual`。
- **會觸發誰**：重複呼叫 FN-07 直到達到指定數量；回傳初始 `Population`。

### FN-03 `GeneticAlgorithm.select(problem, population)`
- **主要行為**：依適應度選出供交配的父母；分析範例採二人錦標賽，允許重複抽選。
- **觸發時機**：每一代交配之前。
- **被誰觸發**：FN-01。
- **協作對象**：`Population`、`Individual`、`Fitness`、`OptimizationProblem`。
- **會觸發誰**：透過 FN-08 評估被抽中的個體並比較，回傳至少兩個父母供 FN-04 使用；FN-01 負責接續呼叫 FN-04。

### FN-04 `GeneticAlgorithm.crossover(problem, parents, populationSize)`
- **主要行為**：配對父母並建立指定數量的後代，組成新種群。
- **觸發時機**：FN-03 回傳父母後。
- **被誰觸發**：FN-01。
- **協作對象**：父母 `Individual`、`OptimizationProblem`、後代 `Population`。
- **會觸發誰**：對選出的父母呼叫 FN-09 產生後代；若本次不交配，使用父母個體的獨立副本。回傳後由 FN-01 呼叫 FN-05。

### FN-05 `GeneticAlgorithm.mutate(problem, population)`
- **主要行為**：依變異率處理後代並組成新種群，不修改原父母。
- **觸發時機**：FN-04 建立後代種群後。
- **被誰觸發**：FN-01。
- **協作對象**：後代 `Population`、`Individual`、`OptimizationProblem`。
- **會觸發誰**：對選中變異的後代呼叫 FN-10；其餘保留原後代。回傳新種群給 FN-01 進行終止判斷或下一代演化。

### FN-06 `GeneticAlgorithm.findBest(problem, population)`
- **主要行為**：評估最終種群，回傳分數最高的可行個體；若無可行個體則回報無可行解。
- **觸發時機**：演化停止後。
- **被誰觸發**：FN-01。
- **協作對象**：`Population`、`Individual`、`OptimizationProblem`、`Fitness`。
- **會觸發誰**：對每個個體呼叫 FN-08；將結果回傳 FN-01。不得聲稱此結果必為全域最佳解。

## 問題共同行為契約

### FN-07 `OptimizationProblem.createIndividual()`
- **主要行為**：依問題資料產生一個初始候選解。
- **觸發時機**：建立初始種群時。
- **被誰觸發**：FN-02。
- **協作對象**：具體問題及其資料、`Individual`、`Chromosome`、`Gene`。
- **會觸發誰**：依問題實際型別執行 FN-11 或 FN-15，回傳新個體。

### FN-08 `OptimizationProblem.evaluate(individual)`
- **主要行為**：依問題限制及目標計算候選解可行性與適應度。
- **觸發時機**：篩選比較及尋找最終結果時。
- **被誰觸發**：FN-03、FN-06。
- **協作對象**：`Individual`、具體問題資料、`Fitness`。
- **會觸發誰**：依問題實際型別執行 FN-12 或 FN-16，回傳評估結果。

### FN-09 `OptimizationProblem.crossover(parent1, parent2)`
- **主要行為**：依該問題的染色體表示法，從兩個父母產生一個新個體。
- **觸發時機**：FN-04 選中父母交配時。
- **被誰觸發**：FN-04。
- **協作對象**：兩個父母的 `Chromosome`、`Gene`，及問題資料。
- **會觸發誰**：依問題實際型別執行 FN-13 或 FN-17，回傳後代；不得修改父母。

### FN-10 `OptimizationProblem.mutate(individual)`
- **主要行為**：依該問題的染色體表示法，回傳基因改變後的新個體。
- **觸發時機**：FN-05 選中後代變異時。
- **被誰觸發**：FN-05。
- **協作對象**：後代的 `Chromosome`、`Gene`，及問題資料。
- **會觸發誰**：依問題實際型別執行 FN-14 或 FN-18，回傳變異後個體。

## 生產排程情境

### FN-11 `SchedulingProblem.createIndividual()`
- **主要行為**：依 A、B、C 需求數量建立生產任務，安排機器、工人與開始／結束時間，將任務編入染色體。可藉由依序派工避免資源時間重疊。
- **觸發時機**：建立排程初始種群時。
- **被誰觸發**：FN-07，由 FN-02 呼叫。
- **協作對象**：`ProductionDemand`、`ManufacturedProduct`、`Machine`、`Worker`、`ProductionTask`、`Individual`。
- **會觸發誰**：建立基因與個體並回傳 FN-02；不自行啟動演化。

### FN-12 `SchedulingProblem.evaluate(individual)`
- **主要行為**：檢查產品需求數量、任務時長、機器及工人時間是否衝突；可行時以負的最後完工時間作為範例分數，完工越早分數越高。
- **觸發時機**：篩選或選取最終排程時。
- **被誰觸發**：FN-08，由 FN-03 或 FN-06 呼叫。
- **協作對象**：個體中的 `ProductionTask`、`ProductionDemand`、`Machine`、`Worker`。
- **會觸發誰**：回傳 `Fitness`；成本資料及與完工時間的權衡未由題目提供，不能把完工時間分數宣稱為成本公式。

### FN-13 `SchedulingProblem.crossover(parent1, parent2)`
- **主要行為**：以父母的任務順序產生子代任務順序，保留各產品需求數量，再依可用機器與工人重新安排時間，產生新個體。
- **觸發時機**：排程父母被選中交配時。
- **被誰觸發**：FN-09，由 FN-04 呼叫。
- **協作對象**：父母染色體、`ProductionDemand`、`Machine`、`Worker`、`ProductionTask`。
- **會觸發誰**：建立並回傳後代；其可行性與分數之後由 FN-12 評估。

### FN-14 `SchedulingProblem.mutate(individual)`
- **主要行為**：例如交換兩個生產任務順序，再依資源可用時間重新派工，產生新個體。
- **觸發時機**：排程後代被選中變異時。
- **被誰觸發**：FN-10，由 FN-05 呼叫。
- **協作對象**：後代任務基因、`Machine`、`Worker`。
- **會觸發誰**：建立並回傳變異後個體；其可行性與分數之後由 FN-12 評估。

## 商品推薦情境

### FN-15 `RecommendationProblem.createIndividual()`
- **主要行為**：從候選商品建立推薦基因序列，可重複選同一商品；產生時考量預算及承重。
- **觸發時機**：建立推薦初始種群時。
- **被誰觸發**：FN-07，由 FN-02 呼叫。
- **協作對象**：候選 `Product`、預算、承重、`Individual`、`Gene`。
- **會觸發誰**：建立並回傳個體；允許空清單作為可行候選解。

### FN-16 `RecommendationProblem.evaluate(individual)`
- **主要行為**：加總商品價格及重量，超出預算或承重即不可行；可行時以每個商品的類別喜好度加總作為範例分數，重複商品逐件計入。
- **觸發時機**：篩選或選取最終清單時。
- **被誰觸發**：FN-08，由 FN-03 或 FN-06 呼叫。
- **協作對象**：個體商品基因、`ProductCategory`、`CategoryPreference`、預算及承重。
- **會觸發誰**：回傳 `Fitness`。範例清單產品 1 兩件、產品 4 一件、產品 5 一件為 680 元、14 公斤，範例分數為 2.4；此公式是本分析假設，不是題目給定公式。

### FN-17 `RecommendationProblem.crossover(parent1, parent2)`
- **主要行為**：以父母商品基因片段組合新清單；若超出限制，可移除商品直到可行，再產生後代。
- **觸發時機**：推薦父母被選中交配時。
- **被誰觸發**：FN-09，由 FN-04 呼叫。
- **協作對象**：父母染色體、`Product`、預算與承重。
- **會觸發誰**：建立並回傳後代；其適應度之後由 FN-16 評估。

### FN-18 `RecommendationProblem.mutate(individual)`
- **主要行為**：例如隨機新增、移除或替換一個商品；超出預算或承重時修復成可行清單，產生新個體。
- **觸發時機**：推薦後代被選中變異時。
- **被誰觸發**：FN-10，由 FN-05 呼叫。
- **協作對象**：後代商品基因、候選 `Product`、預算與承重。
- **會觸發誰**：建立並回傳變異後個體；其適應度之後由 FN-16 評估。

## 尚待決定的題目缺口

- 排程成本的資料來源、成本公式及與完工時間的權衡；目前範例只評估完工時間。
- 推薦與既有購物清單的「相關」定義、現有清單是否已消耗預算與承重；未定義前假設候選商品已由呼叫端篩選，預算與承重為可用餘額。
- 喜好度缺值的處理、隨機種子、交配率、變異率、非上限的終止條件及無可行解的具體回報型別，須於實作前訂定。
