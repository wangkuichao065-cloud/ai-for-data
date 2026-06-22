// ============================================================
// Neo4j 知识图谱初始化脚本
// 数据库: knowledge_graph
// 执行方式: 在 Neo4j Browser 中逐段粘贴执行
// ============================================================

// === 1. 创建唯一约束 ===
CREATE CONSTRAINT course_id IF NOT EXISTS FOR (n:Course) REQUIRE n.node_id IS UNIQUE;
CREATE CONSTRAINT chapter_id IF NOT EXISTS FOR (n:Chapter) REQUIRE n.node_id IS UNIQUE;
CREATE CONSTRAINT kp_id IF NOT EXISTS FOR (n:KnowledgePoint) REQUIRE n.node_id IS UNIQUE;
CREATE CONSTRAINT algo_id IF NOT EXISTS FOR (n:Algorithm) REQUIRE n.node_id IS UNIQUE;
CREATE CONSTRAINT app_id IF NOT EXISTS FOR (n:Application) REQUIRE n.node_id IS UNIQUE;

// === 2. 创建课程节点 ===
CREATE (:Course {node_id: 'course_ml', name: '机器学习', code: 'CS301', description: '研究计算机系统如何自动改进的学科', credit: 3.0, semester: '2026春季'});
CREATE (:Course {node_id: 'course_dm', name: '数据挖掘', code: 'CS302', description: '从大量数据中发现模式和知识', credit: 3.0, semester: '2026春季'});

// === 3. 创建章节节点 ===
CREATE (:Chapter {node_id: 'ch_ml_01', name: '监督学习', order: 1, description: '利用标注数据训练模型'});
CREATE (:Chapter {node_id: 'ch_ml_02', name: '无监督学习', order: 2, description: '从无标签数据中发现模式'});
CREATE (:Chapter {node_id: 'ch_ml_03', name: '深度学习', order: 3, description: '基于神经网络的机器学习方法'});
CREATE (:Chapter {node_id: 'ch_dm_01', name: '关联规则', order: 1, description: '发现项之间的关联关系'});
CREATE (:Chapter {node_id: 'ch_dm_02', name: '分类与预测', order: 2, description: '构建分类模型进行预测'});
CREATE (:Chapter {node_id: 'ch_dm_03', name: '降维', order: 3, description: '减少数据维度同时保留信息'});

// === 4. 课程→章节包含关系 ===
MATCH (c:Course {node_id: 'course_ml'}), (ch:Chapter {node_id: 'ch_ml_01'}) CREATE (c)-[:CONTAINS {order: 1}]->(ch);
MATCH (c:Course {node_id: 'course_ml'}), (ch:Chapter {node_id: 'ch_ml_02'}) CREATE (c)-[:CONTAINS {order: 2}]->(ch);
MATCH (c:Course {node_id: 'course_ml'}), (ch:Chapter {node_id: 'ch_ml_03'}) CREATE (c)-[:CONTAINS {order: 3}]->(ch);
MATCH (c:Course {node_id: 'course_dm'}), (ch:Chapter {node_id: 'ch_dm_01'}) CREATE (c)-[:CONTAINS {order: 1}]->(ch);
MATCH (c:Course {node_id: 'course_dm'}), (ch:Chapter {node_id: 'ch_dm_02'}) CREATE (c)-[:CONTAINS {order: 2}]->(ch);
MATCH (c:Course {node_id: 'course_dm'}), (ch:Chapter {node_id: 'ch_dm_03'}) CREATE (c)-[:CONTAINS {order: 3}]->(ch);

// === 5. 创建知识点节点（机器学习） ===
CREATE (:KnowledgePoint {node_id: 'kp_lr', name: '线性回归', description: '通过线性关系建模变量间关系', difficulty: 2, importance: 4, keywords: ['最小二乘法', '线性模型', '回归']});
CREATE (:KnowledgePoint {node_id: 'kp_logr', name: '逻辑回归', description: '用于二分类的对数线性模型', difficulty: 3, importance: 5, keywords: ['Sigmoid', '分类', '对数损失']});
CREATE (:KnowledgePoint {node_id: 'kp_svm', name: '支持向量机', description: '寻找最大间隔超平面的二分类模型', difficulty: 4, importance: 5, keywords: ['SVM', '核函数', '最大间隔']});
CREATE (:KnowledgePoint {node_id: 'kp_kernel', name: '核函数', description: '将数据映射到高维空间的函数', difficulty: 4, importance: 4, keywords: ['RBF', '多项式核', '核技巧']});
CREATE (:KnowledgePoint {node_id: 'kp_dt', name: '决策树', description: '基于树结构进行决策的算法', difficulty: 3, importance: 4, keywords: ['ID3', 'C4.5', 'CART', '信息增益']});
CREATE (:KnowledgePoint {node_id: 'kp_rf', name: '随机森林', description: '基于多棵决策树的集成学习算法', difficulty: 3, importance: 4, keywords: ['集成学习', 'Bagging', '随机特征']});
CREATE (:KnowledgePoint {node_id: 'kp_kmeans', name: 'K-Means聚类', description: '基于距离的划分式聚类算法', difficulty: 2, importance: 4, keywords: ['聚类', '质心', '距离']});
CREATE (:KnowledgePoint {node_id: 'kp_dbscan', name: 'DBSCAN', description: '基于密度的聚类算法', difficulty: 3, importance: 3, keywords: ['密度', '核心点', '噪声']});
CREATE (:KnowledgePoint {node_id: 'kp_cnn', name: '卷积神经网络', description: '用于图像处理的深度学习模型', difficulty: 5, importance: 5, keywords: ['CNN', '卷积', '池化', '特征提取']});
CREATE (:KnowledgePoint {node_id: 'kp_rnn', name: '循环神经网络', description: '处理序列数据的神经网络', difficulty: 5, importance: 4, keywords: ['RNN', 'LSTM', '序列']});
CREATE (:KnowledgePoint {node_id: 'kp_nn', name: '神经网络基础', description: '神经元、激活函数、前向传播和反向传播', difficulty: 4, importance: 5, keywords: ['激活函数', '反向传播', '梯度下降']});
CREATE (:KnowledgePoint {node_id: 'kp_bp', name: '反向传播算法', description: '通过链式法则计算梯度的神经网络训练算法', difficulty: 4, importance: 5, keywords: ['梯度下降', '链式法则', '梯度']});

// === 6. 创建知识点节点（数据挖掘） ===
CREATE (:KnowledgePoint {node_id: 'kp_apriori', name: 'Apriori算法', description: '基于频繁项集的关联规则挖掘算法', difficulty: 3, importance: 4, keywords: ['关联规则', '频繁项集', '支持度']});
CREATE (:KnowledgePoint {node_id: 'kp_fpgrowth', name: 'FP-Growth', description: '基于FP树的频繁模式增长算法', difficulty: 4, importance: 3, keywords: ['FP树', '频繁模式', '条件树']});
CREATE (:KnowledgePoint {node_id: 'kp_nb', name: '朴素贝叶斯', description: '基于贝叶斯定理的分类算法', difficulty: 2, importance: 3, keywords: ['贝叶斯', '条件概率', '文本分类']});
CREATE (:KnowledgePoint {node_id: 'kp_xgboost', name: 'XGBoost', description: '高效的梯度提升决策树算法', difficulty: 4, importance: 4, keywords: ['梯度提升', '正则化', 'GBDT']});
CREATE (:KnowledgePoint {node_id: 'kp_pca', name: '主成分分析', description: '通过线性变换降维的方法', difficulty: 4, importance: 4, keywords: ['PCA', '降维', '特征值']});
CREATE (:KnowledgePoint {node_id: 'kp_tsne', name: 't-SNE', description: '非线性降维方法，适合可视化', difficulty: 4, importance: 3, keywords: ['t-SNE', '降维', '可视化']});
CREATE (:KnowledgePoint {node_id: 'kp_knn', name: 'K近邻', description: '基于距离的分类算法', difficulty: 1, importance: 3, keywords: ['KNN', '距离', '分类']});
CREATE (:KnowledgePoint {node_id: 'kp_eval', name: '模型评估', description: '准确率、精确率、召回率、F1、ROC曲线', difficulty: 2, importance: 5, keywords: ['准确率', '召回率', 'F1', 'ROC']});

// === 7. 章节→知识点包含关系（机器学习） ===
MATCH (ch:Chapter {node_id: 'ch_ml_01'}), (kp:KnowledgePoint {node_id: 'kp_lr'}) CREATE (ch)-[:CONTAINS]->(kp);
MATCH (ch:Chapter {node_id: 'ch_ml_01'}), (kp:KnowledgePoint {node_id: 'kp_logr'}) CREATE (ch)-[:CONTAINS]->(kp);
MATCH (ch:Chapter {node_id: 'ch_ml_01'}), (kp:KnowledgePoint {node_id: 'kp_svm'}) CREATE (ch)-[:CONTAINS]->(kp);
MATCH (ch:Chapter {node_id: 'ch_ml_01'}), (kp:KnowledgePoint {node_id: 'kp_kernel'}) CREATE (ch)-[:CONTAINS]->(kp);
MATCH (ch:Chapter {node_id: 'ch_ml_01'}), (kp:KnowledgePoint {node_id: 'kp_dt'}) CREATE (ch)-[:CONTAINS]->(kp);
MATCH (ch:Chapter {node_id: 'ch_ml_01'}), (kp:KnowledgePoint {node_id: 'kp_rf'}) CREATE (ch)-[:CONTAINS]->(kp);
MATCH (ch:Chapter {node_id: 'ch_ml_01'}), (kp:KnowledgePoint {node_id: 'kp_knn'}) CREATE (ch)-[:CONTAINS]->(kp);
MATCH (ch:Chapter {node_id: 'ch_ml_02'}), (kp:KnowledgePoint {node_id: 'kp_kmeans'}) CREATE (ch)-[:CONTAINS]->(kp);
MATCH (ch:Chapter {node_id: 'ch_ml_02'}), (kp:KnowledgePoint {node_id: 'kp_dbscan'}) CREATE (ch)-[:CONTAINS]->(kp);
MATCH (ch:Chapter {node_id: 'ch_ml_03'}), (kp:KnowledgePoint {node_id: 'kp_nn'}) CREATE (ch)-[:CONTAINS]->(kp);
MATCH (ch:Chapter {node_id: 'ch_ml_03'}), (kp:KnowledgePoint {node_id: 'kp_bp'}) CREATE (ch)-[:CONTAINS]->(kp);
MATCH (ch:Chapter {node_id: 'ch_ml_03'}), (kp:KnowledgePoint {node_id: 'kp_cnn'}) CREATE (ch)-[:CONTAINS]->(kp);
MATCH (ch:Chapter {node_id: 'ch_ml_03'}), (kp:KnowledgePoint {node_id: 'kp_rnn'}) CREATE (ch)-[:CONTAINS]->(kp);

// === 8. 章节→知识点包含关系（数据挖掘） ===
MATCH (ch:Chapter {node_id: 'ch_dm_01'}), (kp:KnowledgePoint {node_id: 'kp_apriori'}) CREATE (ch)-[:CONTAINS]->(kp);
MATCH (ch:Chapter {node_id: 'ch_dm_01'}), (kp:KnowledgePoint {node_id: 'kp_fpgrowth'}) CREATE (ch)-[:CONTAINS]->(kp);
MATCH (ch:Chapter {node_id: 'ch_dm_02'}), (kp:KnowledgePoint {node_id: 'kp_nb'}) CREATE (ch)-[:CONTAINS]->(kp);
MATCH (ch:Chapter {node_id: 'ch_dm_02'}), (kp:KnowledgePoint {node_id: 'kp_xgboost'}) CREATE (ch)-[:CONTAINS]->(kp);
MATCH (ch:Chapter {node_id: 'ch_dm_02'}), (kp:KnowledgePoint {node_id: 'kp_eval'}) CREATE (ch)-[:CONTAINS]->(kp);
MATCH (ch:Chapter {node_id: 'ch_dm_03'}), (kp:KnowledgePoint {node_id: 'kp_pca'}) CREATE (ch)-[:CONTAINS]->(kp);
MATCH (ch:Chapter {node_id: 'ch_dm_03'}), (kp:KnowledgePoint {node_id: 'kp_tsne'}) CREATE (ch)-[:CONTAINS]->(kp);

// === 9. 知识点→课程归属 ===
MATCH (kp:KnowledgePoint), (c:Course {node_id: 'course_ml'})
WHERE kp.node_id IN ['kp_lr','kp_logr','kp_svm','kp_kernel','kp_dt','kp_rf','kp_kmeans','kp_dbscan','kp_cnn','kp_rnn','kp_nn','kp_bp','kp_knn','kp_eval']
CREATE (kp)-[:BELONGS_TO]->(c);

MATCH (kp:KnowledgePoint), (c:Course {node_id: 'course_dm'})
WHERE kp.node_id IN ['kp_apriori','kp_fpgrowth','kp_nb','kp_xgboost','kp_pca','kp_tsne','kp_knn','kp_eval']
CREATE (kp)-[:BELONGS_TO]->(c);

// === 10. 知识点依赖关系 ===
MATCH (kp1:KnowledgePoint {node_id: 'kp_svm'}), (kp2:KnowledgePoint {node_id: 'kp_kernel'}) CREATE (kp1)-[:DEPENDS_ON {strength: 'strong'}]->(kp2);
MATCH (kp1:KnowledgePoint {node_id: 'kp_cnn'}), (kp2:KnowledgePoint {node_id: 'kp_nn'}) CREATE (kp1)-[:DEPENDS_ON {strength: 'strong'}]->(kp2);
MATCH (kp1:KnowledgePoint {node_id: 'kp_rnn'}), (kp2:KnowledgePoint {node_id: 'kp_nn'}) CREATE (kp1)-[:DEPENDS_ON {strength: 'strong'}]->(kp2);
MATCH (kp1:KnowledgePoint {node_id: 'kp_cnn'}), (kp2:KnowledgePoint {node_id: 'kp_bp'}) CREATE (kp1)-[:DEPENDS_ON {strength: 'medium'}]->(kp2);
MATCH (kp1:KnowledgePoint {node_id: 'kp_rnn'}), (kp2:KnowledgePoint {node_id: 'kp_bp'}) CREATE (kp1)-[:DEPENDS_ON {strength: 'medium'}]->(kp2);
MATCH (kp1:KnowledgePoint {node_id: 'kp_bp'}), (kp2:KnowledgePoint {node_id: 'kp_nn'}) CREATE (kp1)-[:DEPENDS_ON {strength: 'strong'}]->(kp2);
MATCH (kp1:KnowledgePoint {node_id: 'kp_rf'}), (kp2:KnowledgePoint {node_id: 'kp_dt'}) CREATE (kp1)-[:DEPENDS_ON {strength: 'strong'}]->(kp2);
MATCH (kp1:KnowledgePoint {node_id: 'kp_logr'}), (kp2:KnowledgePoint {node_id: 'kp_lr'}) CREATE (kp1)-[:DEPENDS_ON {strength: 'medium'}]->(kp2);
MATCH (kp1:KnowledgePoint {node_id: 'kp_fpgrowth'}), (kp2:KnowledgePoint {node_id: 'kp_apriori'}) CREATE (kp1)-[:DEPENDS_ON {strength: 'medium'}]->(kp2);
MATCH (kp1:KnowledgePoint {node_id: 'kp_xgboost'}), (kp2:KnowledgePoint {node_id: 'kp_dt'}) CREATE (kp1)-[:DEPENDS_ON {strength: 'strong'}]->(kp2);

// === 11. 知识点相似关系 ===
MATCH (kp1:KnowledgePoint {node_id: 'kp_lr'}), (kp2:KnowledgePoint {node_id: 'kp_logr'}) CREATE (kp1)-[:SIMILAR_TO {similarity: 0.85, dimension: '原理'}]->(kp2);
MATCH (kp1:KnowledgePoint {node_id: 'kp_svm'}), (kp2:KnowledgePoint {node_id: 'kp_logr'}) CREATE (kp1)-[:SIMILAR_TO {similarity: 0.70, dimension: '应用'}]->(kp2);
MATCH (kp1:KnowledgePoint {node_id: 'kp_cnn'}), (kp2:KnowledgePoint {node_id: 'kp_rnn'}) CREATE (kp1)-[:SIMILAR_TO {similarity: 0.75, dimension: '原理'}]->(kp2);
MATCH (kp1:KnowledgePoint {node_id: 'kp_kmeans'}), (kp2:KnowledgePoint {node_id: 'kp_dbscan'}) CREATE (kp1)-[:SIMILAR_TO {similarity: 0.65, dimension: '应用'}]->(kp2);
MATCH (kp1:KnowledgePoint {node_id: 'kp_dt'}), (kp2:KnowledgePoint {node_id: 'kp_rf'}) CREATE (kp1)-[:SIMILAR_TO {similarity: 0.80, dimension: '原理'}]->(kp2);
MATCH (kp1:KnowledgePoint {node_id: 'kp_pca'}), (kp2:KnowledgePoint {node_id: 'kp_tsne'}) CREATE (kp1)-[:SIMILAR_TO {similarity: 0.70, dimension: '应用'}]->(kp2);
MATCH (kp1:KnowledgePoint {node_id: 'kp_apriori'}), (kp2:KnowledgePoint {node_id: 'kp_fpgrowth'}) CREATE (kp1)-[:SIMILAR_TO {similarity: 0.75, dimension: '原理'}]->(kp2);
MATCH (kp1:KnowledgePoint {node_id: 'kp_nb'}), (kp2:KnowledgePoint {node_id: 'kp_logr'}) CREATE (kp1)-[:SIMILAR_TO {similarity: 0.55, dimension: '应用'}]->(kp2);

// === 12. 创建算法节点 ===
CREATE (:Algorithm {node_id: 'algo_ols', name: '最小二乘法', full_name: '普通最小二乘法', description: '通过最小化残差平方和求解回归系数', time_complexity: 'O(n*p^2)', space_complexity: 'O(p^2)', pros: '计算简单，可解释性强', cons: '对异常值敏感，假设线性关系'});
CREATE (:Algorithm {node_id: 'algo_smo', name: 'SMO', full_name: '序列最小优化算法', description: '用于训练SVM的分解算法', time_complexity: 'O(n^2)~O(n^3)', space_complexity: 'O(n^2)', pros: '高效求解SVM对偶问题', cons: '大规模数据较慢'});
CREATE (:Algorithm {node_id: 'algo_id3', name: 'ID3', full_name: '迭代二分器3', description: '基于信息增益构建决策树', time_complexity: 'O(n*d*log(n))', space_complexity: 'O(n*d)', pros: '直观易懂', cons: '只能处理离散特征，易过拟合'});
CREATE (:Algorithm {node_id: 'algo_cart', name: 'CART', full_name: '分类与回归树', description: '基于基尼系数构建二叉决策树', time_complexity: 'O(n*d*log(n))', space_complexity: 'O(n*d)', pros: '支持分类和回归', cons: '易过拟合'});
CREATE (:Algorithm {node_id: 'algo_kmeans', name: 'K-Means', full_name: 'K均值聚类', description: '基于距离的划分式聚类算法', time_complexity: 'O(n*k*t)', space_complexity: 'O(n+k)', pros: '简单高效，适合大规模数据', cons: '需预先指定K值，对初始点敏感'});
CREATE (:Algorithm {node_id: 'algo_apriori', name: 'Apriori', full_name: 'Apriori算法', description: '逐层搜索频繁项集的关联规则算法', time_complexity: 'O(2^n)', space_complexity: 'O(2^n)', pros: '原理简单易于实现', cons: '候选项集过多，效率较低'});
CREATE (:Algorithm {node_id: 'algo_fpgrowth', name: 'FP-Growth', full_name: '频繁模式增长', description: '基于FP树的高效频繁模式挖掘算法', time_complexity: 'O(n*d)', space_complexity: 'O(n*d)', pros: '无需候选集，效率高', cons: 'FP树构建复杂'});
CREATE (:Algorithm {node_id: 'algo_gd', name: '梯度下降', full_name: '梯度下降法', description: '沿梯度反方向迭代更新参数的优化算法', time_complexity: 'O(n*iter)', space_complexity: 'O(n)', pros: '通用性强', cons: '可能陷入局部最优，学习率敏感'});

// === 13. 知识点→算法实现关系 ===
MATCH (kp:KnowledgePoint {node_id: 'kp_lr'}), (a:Algorithm {node_id: 'algo_ols'}) CREATE (kp)-[:IMPLEMENTS]->(a);
MATCH (kp:KnowledgePoint {node_id: 'kp_svm'}), (a:Algorithm {node_id: 'algo_smo'}) CREATE (kp)-[:IMPLEMENTS]->(a);
MATCH (kp:KnowledgePoint {node_id: 'kp_dt'}), (a:Algorithm {node_id: 'algo_id3'}) CREATE (kp)-[:IMPLEMENTS]->(a);
MATCH (kp:KnowledgePoint {node_id: 'kp_dt'}), (a:Algorithm {node_id: 'algo_cart'}) CREATE (kp)-[:IMPLEMENTS]->(a);
MATCH (kp:KnowledgePoint {node_id: 'kp_kmeans'}), (a:Algorithm {node_id: 'algo_kmeans'}) CREATE (kp)-[:IMPLEMENTS]->(a);
MATCH (kp:KnowledgePoint {node_id: 'kp_apriori'}), (a:Algorithm {node_id: 'algo_apriori'}) CREATE (kp)-[:IMPLEMENTS]->(a);
MATCH (kp:KnowledgePoint {node_id: 'kp_fpgrowth'}), (a:Algorithm {node_id: 'algo_fpgrowth'}) CREATE (kp)-[:IMPLEMENTS]->(a);
MATCH (kp:KnowledgePoint {node_id: 'kp_nn'}), (a:Algorithm {node_id: 'algo_gd'}) CREATE (kp)-[:IMPLEMENTS]->(a);

// === 14. 创建应用场景节点 ===
CREATE (:Application {node_id: 'app_house', name: '房价预测', description: '使用线性回归预测房屋价格', dataset: 'Boston Housing'});
CREATE (:Application {node_id: 'app_spam', name: '垃圾邮件分类', description: '使用朴素贝叶斯分类邮件', dataset: 'Enron Email'});
CREATE (:Application {node_id: 'app_imgcls', name: '图像分类', description: '使用CNN进行图像分类', dataset: 'CIFAR-10'});
CREATE (:Application {node_id: 'app_customer', name: '客户分群', description: '使用K-Means对客户聚类', dataset: 'Mall Customers'});
CREATE (:Application {node_id: 'app_rec', name: '商品推荐', description: '使用关联规则进行商品推荐', dataset: 'Grocery Transactions'});
CREATE (:Application {node_id: 'app_nlp', name: '文本情感分析', description: '使用RNN/LSTM分析文本情感', dataset: 'IMDB Reviews'});
CREATE (:Application {node_id: 'app_medical', name: '疾病诊断', description: '使用决策树辅助疾病诊断', dataset: 'Breast Cancer'});
CREATE (:Application {node_id: 'app_fraud', name: '欺诈检测', description: '使用XGBoost检测信用卡欺诈', dataset: 'Credit Card Fraud'});

// === 15. 知识点→应用关系 ===
MATCH (kp:KnowledgePoint {node_id: 'kp_lr'}), (app:Application {node_id: 'app_house'}) CREATE (kp)-[:APPLIED_TO]->(app);
MATCH (kp:KnowledgePoint {node_id: 'kp_nb'}), (app:Application {node_id: 'app_spam'}) CREATE (kp)-[:APPLIED_TO]->(app);
MATCH (kp:KnowledgePoint {node_id: 'kp_cnn'}), (app:Application {node_id: 'app_imgcls'}) CREATE (kp)-[:APPLIED_TO]->(app);
MATCH (kp:KnowledgePoint {node_id: 'kp_kmeans'}), (app:Application {node_id: 'app_customer'}) CREATE (kp)-[:APPLIED_TO]->(app);
MATCH (kp:KnowledgePoint {node_id: 'kp_apriori'}), (app:Application {node_id: 'app_rec'}) CREATE (kp)-[:APPLIED_TO]->(app);
MATCH (kp:KnowledgePoint {node_id: 'kp_rnn'}), (app:Application {node_id: 'app_nlp'}) CREATE (kp)-[:APPLIED_TO]->(app);
MATCH (kp:KnowledgePoint {node_id: 'kp_dt'}), (app:Application {node_id: 'app_medical'}) CREATE (kp)-[:APPLIED_TO]->(app);
MATCH (kp:KnowledgePoint {node_id: 'kp_xgboost'}), (app:Application {node_id: 'app_fraud'}) CREATE (kp)-[:APPLIED_TO]->(app);

// === 16. 验证查询 ===
// 查看节点总数
MATCH (n) RETURN count(n) AS total_nodes;
// 查看关系总数
MATCH ()-[r]->() RETURN count(r) AS total_edges;
// 查看各类型节点数
MATCH (n) RETURN labels(n)[0] AS type, count(n) AS count;
// 查看各关系类型数
MATCH ()-[r]->() RETURN type(r) AS relation, count(r) AS count;
