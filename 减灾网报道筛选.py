# 本代码用于筛选从减灾网爬取到的报道的内容

# 筛选暴雨、洪涝相关的数据
import pandas as pd
df_art_cont=pd.read_csv("./article_content.csv",encoding="utf-8")

# 筛选出title字段中包含“洪涝”一词的记录，存储新的dataframe中
df_filter_art= df_art_cont[(df_art_cont.title.str.contains('洪涝'))]

# 将筛选后的数据存入到flood_article.csv中
df_filter_art.to_csv("./flood_content.csv",encoding="utf-8",index=False,header=True)


