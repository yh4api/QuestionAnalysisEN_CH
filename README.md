# QuestionAnalysisEN_CH

Code for natural language question decomposition:<br/>
-- dependency <br/>
EN: stanford-corenlp <br/>
CH: jieba <br/>

Chinese question example: <br/>
幫我找關於monte carlo演算法的文章 <br/>
我要找跟AlphaGo有關的新聞 <br/>
我要找會 Autocad, Matlab 和 deep learning的front end工程師 <br/>
推薦我一些文件 <br/>
推薦我一些勵志小說 <br/>

Tested: <br/>
英文 中文 <br/>
show me some data mining papers 列出收集的文章資料 <br/>
show me the lastest big data news 列出大數據新聞 <br/>
show me some 2015 big data news 列出2015大數據新聞 <br/>
display some news about big data 播放關於大數據的新聞 <br/>

give me a list containing the latest big data news 給我最近的大數據新聞 <br/>
could you recommend me/us some papers about machine learning 可以推薦一些機器學習的文件給我嗎? <br/>
could you suggest some papers about machine learning and mahout (for me/us) <= is it possible to add indirect object automatically? 可以推薦一些machine learning 和 mahout的文件給我嗎? <br/>

who is good at java? 誰很擅長java? <br/>
who is good at java and c# and sql? 誰會java C# 和 sql <br/>
who is good at java or c# or sql? 誰會java 或 c# 或 sql <br/>
who knows about java? 誰很會java <br/>
please recommend some java experts 請推薦一些java工程師 <br/>
do you know anyone good at Java? 你知道有誰精通java <br/>

Its ability for real case:<br/>
Please give me some papers of cloud computing after May20, 2012=> look for information, time May 20, 2012 to present<br/>
Show me some information about computer science since 2005 => look for information, time 2005 to present<br/>
Show me some information about computer science from 2005 to 2013 => look for information, time 2005 to 2013<br/>
Show me some papers of computer science published by MIT => look for papers, Author MIT<br/>
Can you give me some books written by Mark => look for book, Author Mark<br/>
Do you have brothers or sisters => I don;t answer personal questions.<br/>
請搜尋執行過三個大型專案的網頁設計師 => look for 人(網頁設計師), 大型專案<br/>

