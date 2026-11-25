# 基因演算法 OOD 函式與協作規格

對應 [OOD.MMD](./OOD.MMD)，承接 [OOA](./OOA-EN.MMD) 與 [原始題目](./readme2.md)。`D01` 等 ID 是本圖獨立編號。類別圖中的單純資料讀取器只提供不可修改的值或唯讀集合，不列為業務函式。

## 設計與資料契約

- **工廠方法**：`GeneticAlgorithm.solve` 在初始化流程需要新個體時呼叫 `createIndividual`（D02）；`SchedulingGA`、`RecommendationGA` 覆寫此方法。演算法決定建立時機與數量，子類別決定建立哪個情境的個體。
- **策略**：`Selection` 由演算法組合，預設為二人錦標賽；`GeneticProblem` 封裝適應度、交配及變異的情境規則。新增問題可實作 `GeneticProblem` 並新增 `GeneticAlgorithm` 子類別，而不用修改套件。
- `G` 是基因值的型別，`Individual<G>` 包含不可變 `Chromosome<G>`；其基因清單及 `Population<G>` 清單均不可修改。基因元素是不可變值。演算操作回傳新個體或沿用不可變個體，不得修改父母或舊種群。圖中泛型的關聯以型別參數為準。
- `Fitness` 用字典序比較 `(feasible, score)`：可行優先，同可行性比較 score，數值越大越好；分數不可為 NaN 或無窮大。所有評估皆依目前個體重新計算。最終種群若無可行解，`solve` 回傳 `Optional.empty()`；空推薦清單可行。
- `GAConfig`：種群大小至少 2、最大迭代次數至少 0、交配及變異率介於 0 到 1；無效設定在建構時拒絕。單一注入的 `Random` 提供所有隨機選擇，使用相同種子與相同輸入可重現。以最大迭代次數終止，0 代表直接評估初始種群。
- 排程基因是 `ProductionProduct` 序列：各產品出現次數必須等於需求數量。`decode` 從序列產生有機器、工人與時間的排程；這比 OOA 的 `ProductionTask` 基因更容易保持需求數量並避免直接交叉時間表。推薦基因是 `Product`，重複基因代表多件商品。
- 兩情境在呼叫前由應用程式組裝問題、選擇器、設定與隨機來源。`SchedulingGA` 與 `RecommendationGA` 分別持有同一個傳給基底類別的具體問題，供工廠方法委派。回傳的排程個體可再呼叫 D18 取得 `Schedule`；推薦個體的基因直接構成推薦清單。

## 共用演算法

### D01 `GeneticAlgorithm.solve()`
- **主要行為**：初始化種群；重複指定代數執行選擇、交配及變異；回傳最終種群中最好的可行個體。
- **觸發時機**：呼叫端要求求解。
- **被誰觸發**：排程或推薦應用程式。
- **協作對象**：`GAConfig`、`Population`、`Selection`、`GeneticProblem`、`Random`。
- **會觸發誰**：D03；每代 D04；結束後 D05。

### D02 `GeneticAlgorithm.createIndividual()`
- **主要行為**：宣告初始化時建立一個 `Individual<G>` 的抽象工廠方法。
- **觸發時機**：每次需要一個初始個體。
- **被誰觸發**：D03。
- **協作對象**：具體 GA 子類別。
- **會觸發誰**：動態派送至 D06 或 D07。這是抽象契約，並非額外執行一次的函式。

### D03 `GeneticAlgorithm.initializePopulation()`
- **主要行為**：建立 `populationSize` 個初始個體並回傳種群。
- **觸發時機**：D01 開始時。
- **被誰觸發**：D01。
- **協作對象**：`GAConfig`、`Population`。
- **會觸發誰**：重複呼叫 D02 共 `populationSize` 次。

### D04 `GeneticAlgorithm.reproduce(population)`
- **主要行為**：從目前種群反覆挑選兩名父母，依交配率產生一名後代或沿用第一名父母；再依變異率產生變異個體，直到新種群大小等於設定值。參數為供選父母的目前種群。
- **觸發時機**：每一代。
- **被誰觸發**：D01。
- **協作對象**：`Selection`、`GeneticProblem`、`Random`、`GAConfig`。
- **會觸發誰**：每個後代呼叫 D11 兩次；交配時呼叫 D09；選中變異時呼叫 D10。未交配時因個體不可變可安全沿用父母。

### D05 `GeneticAlgorithm.findBest(population)`
- **主要行為**：評估最終種群，回傳最佳可行個體；若沒有可行個體則回傳空值。
- **觸發時機**：D01 演化結束。
- **被誰觸發**：D01。
- **協作對象**：`Population`、`GeneticProblem`、`Fitness`。
- **會觸發誰**：對各個體呼叫 D08，再透過 D13 比較。

### D06 `SchedulingGA.createIndividual()`
- **主要行為**：提供排程問題的初始個體。
- **觸發時機**：D03 經 D02 呼叫工廠方法。
- **被誰觸發**：D03。
- **協作對象**：同一個 `SchedulingProblem` 和 `Random`。
- **會觸發誰**：D14，回傳其結果。

### D07 `RecommendationGA.createIndividual()`
- **主要行為**：提供推薦問題的初始個體。
- **觸發時機**：D03 經 D02 呼叫工廠方法。
- **被誰觸發**：D03。
- **協作對象**：同一個 `RecommendationProblem` 和 `Random`。
- **會觸發誰**：D19，回傳其結果。

## 問題行為與選擇契約

### D08 `GeneticProblem.evaluate(individual)`
- **主要行為**：評估個體並回傳 `Fitness`。
- **觸發時機**：選擇父母或決定最終結果時。
- **被誰觸發**：D12、D05。
- **協作對象**：`Individual<G>`、具體問題資料。
- **會觸發誰**：動態派送 D15 或 D20；契約不另外執行。

### D09 `GeneticProblem.crossover(first, second, random)`
- **主要行為**：依具體問題的編碼交配，回傳一名新後代。
- **觸發時機**：D04 的交配機率判定成功時。
- **被誰觸發**：D04。
- **協作對象**：兩個同型別 `Individual<G>`、`Random`。
- **會觸發誰**：動態派送 D16 或 D21。

### D10 `GeneticProblem.mutate(individual, random)`
- **主要行為**：依具體問題的編碼變異，回傳個體。
- **觸發時機**：D04 的變異機率判定成功時。
- **被誰觸發**：D04。
- **協作對象**：`Individual<G>`、`Random`。
- **會觸發誰**：動態派送 D17 或 D22。

### D11 `Selection.select(population, problem, random)`
- **主要行為**：從現有種群挑選一名父母。
- **觸發時機**：D04 每次需要父母時。
- **被誰觸發**：D04。
- **協作對象**：`Population<G>`、`GeneticProblem<G>`、`Random`。
- **會觸發誰**：預設動態派送至 D12；也可替換其他選擇實作。

### D12 `TournamentSelection.select(population, problem, random)`
- **主要行為**：從種群有放回隨機抽兩個個體，依適應度選勝者；同分選第一個。
- **觸發時機**：D04 需要一個父母時。
- **被誰觸發**：D04 經 D11 動態派送。
- **協作對象**：`Population`、`Random`、`GeneticProblem`、`Fitness`。
- **會觸發誰**：各呼叫 D08 評估兩個候選個體，透過 D13 比較。

### D13 `Fitness.compareTo(other)`
- **主要行為**：先比較可行性，再比較分數；正數代表本身較好、零代表相同、負數代表較差。
- **觸發時機**：比較個體表現時。
- **被誰觸發**：D12、D05。
- **協作對象**：另一個 `Fitness`。
- **會觸發誰**：無；回傳比較結果。

## 排程問題

### D14 `SchedulingProblem.createIndividual(random)`
- **主要行為**：依需求數量建立產品基因多重集合，再以 `random` 洗牌；題目資料得到 A 100、B 200、C 300，共 600 個基因。
- **觸發時機**：初始化每個排程個體時。
- **被誰觸發**：D06。
- **協作對象**：`ProductionDemand`、`ProductionProduct`、`Random`、`Chromosome`。
- **會觸發誰**：建立並回傳 `Individual<ProductionProduct>`。

### D15 `SchedulingProblem.evaluate(individual)`
- **主要行為**：檢查產品與數量是否符合需求；不符合即回傳不可行。符合時解碼排程，以負完工小時數為分數，時間越短分數越高。
- **觸發時機**：排程個體參與比較。
- **被誰觸發**：D12 或 D05 經 D08 派送。
- **協作對象**：`ProductionDemand`、`Fitness`、`Schedule`。
- **會觸發誰**：符合需求時呼叫 D18；回傳 `Fitness`。

### D16 `SchedulingProblem.crossover(first, second, random)`
- **主要行為**：採保留數量的一點交配：隨機選切點，先複製第一父母切點前的基因，再按第二父母的順序填入仍缺少的產品，直到各產品達到需求數量。
- **觸發時機**：排程父母被選中交配時。
- **被誰觸發**：D04 經 D09 派送。
- **協作對象**：父母染色體、`ProductionDemand`、`Random`。
- **會觸發誰**：建立並回傳新個體；由後續 D15 評估。

### D17 `SchedulingProblem.mutate(individual, random)`
- **主要行為**：隨機選兩個索引並交換其產品基因，保留產品數量；兩索引相同可不變。
- **觸發時機**：排程後代被選中變異時。
- **被誰觸發**：D04 經 D10 派送。
- **協作對象**：染色體、`Random`。
- **會觸發誰**：建立並回傳個體；由後續 D15 評估。

### D18 `SchedulingProblem.decode(individual)`
- **主要行為**：按基因順序依次選擇最早可用機器及最早可用工人，各自可用時間相同時依 ID 排序；開始時間為兩者可用時間的較大值，結束時間為開始時間加產品工時，更新資源可用時間並記錄任務。完工時間為最晚任務結束時間。
- **觸發時機**：評估有效排程個體，或呼叫端取得最終排程時。
- **被誰觸發**：D15 或排程應用程式。
- **協作對象**：`Individual`、`Machine`、`Worker`、`ProductionTask`、`Schedule`。
- **會觸發誰**：建立並回傳 `Schedule`；機器及工人皆需至少一個，無資源時在問題建立時拒絕。

## 商品推薦問題

### D19 `RecommendationProblem.createIndividual(random)`
- **主要行為**：從空清單開始，隨機從仍可加入且符合剩餘預算和承重的商品中選一件，直到無商品可加入；同商品允許重複。
- **觸發時機**：初始化每個推薦個體時。
- **被誰觸發**：D07。
- **協作對象**：候選 `Product`、預算、承重、`Random`。
- **會觸發誰**：建立並回傳個體；沒有任何可加入商品時回傳空清單。

### D20 `RecommendationProblem.evaluate(individual)`
- **主要行為**：逐件加總價格、重量及類別喜好度；商品不在候選清單或超出任一上限則不可行。可行分數為喜好度總和，重複商品逐件計算。
- **觸發時機**：推薦個體參與比較。
- **被誰觸發**：D12 或 D05 經 D08 派送。
- **協作對象**：`Product`、`Category`、喜好度、`Fitness`。
- **會觸發誰**：回傳 `Fitness`；題目範例 1×2、4×1、5×1 成本 680、重量 14、分數 2.4。

### D21 `RecommendationProblem.crossover(first, second, random)`
- **主要行為**：分別在兩個父母的基因序列隨機選切點（包含兩端），組合第一個前段與第二個後段；從尾端依序移除商品直到不超過預算及承重。
- **觸發時機**：推薦父母被選中交配時。
- **被誰觸發**：D04 經 D09 派送。
- **協作對象**：父母商品清單、`Random`、預算、承重。
- **會觸發誰**：建立並回傳後代；由後續 D20 評估。

### D22 `RecommendationProblem.mutate(individual, random)`
- **主要行為**：隨機選新增、刪除、替換之一；新增或替換從候選商品隨機選取，刪除或替換在非空清單隨機選位置；操作不可執行時保留原清單。完成後從尾端移除商品直到符合限制。
- **觸發時機**：推薦後代被選中變異時。
- **被誰觸發**：D04 經 D10 派送。
- **協作對象**：商品清單、候選商品、`Random`、預算及承重。
- **會觸發誰**：建立並回傳個體；由後續 D20 評估。

## 題目未定義的事項與本設計假設

- 排程成本公式與費率未提供；本設計以完工時間作範例適應度，尚不能宣稱已最佳化實際成本。產品工時需為正整數；需求數量非負，總數須大於零；機器與工人 ID 必須在各自集合內唯一。
- 推薦清單與既有購物清單的「相關性」未定義；假設呼叫端已篩選候選商品且輸入的是可用剩餘預算與承重。預算及承重非負，商品價格及重量為正整數，商品 ID 唯一，各候選商品類別必須有 0 到 1 之間的喜好度；不符合時建立問題即拒絕。
- 喜好度加總、錦標賽及以上交配／變異規則是本設計選擇，並非題目明定。推薦例子中的父代與子代適應度也不足以推導唯一公式。
