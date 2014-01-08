db_config = {
        'USERNAME' :'root',
		'PASSWORD' : '123456',
		'SERVER' :'localhost',
		'NAME' : 'HNInfo'
}

appspot_url='http://codepensieve.appspot.com/'
user_posts_url='http://api.thriftdb.com/api.hnsearch.com/items/_search?%20\%20sortby=create_ts%20dsc%20&limit=100&filter[fields][type]=submission&filter[fields][username]='
user_details_url='http://api.thriftdb.com/api.hnsearch.com/users/'
comments_url='http://api.thriftdb.com/api.hnsearch.com/items/_search?filter[fields][type]=comment&limit=100&filter[fields][discussion.sigid]='
news_url='http://api.thriftdb.com/api.hnsearch.com/items/_search?limit=30&sortby=product%28points,pow%282,div%28div%28ms%28create_ts,NOW%29,3600000%29,72%29%29%29%20desc'
post_url='http://api.thriftdb.com/api.hnsearch.com/items/'