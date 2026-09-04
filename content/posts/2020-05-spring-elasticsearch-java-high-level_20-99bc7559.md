---
title: "Spring 基於 Elasticsearch 搜尋商品 (四) 使用 Java High Level REST Client 新增分詞器與 搜尋"
date: "2020-05-20T22:55:00.001+08:00"
updated: "2020-07-07T07:35:46.353+08:00"
permalink: "/2020/05/spring-elasticsearch-java-high-level_20.html"
original_url: "https://x8795278.blogspot.com/2020/05/spring-elasticsearch-java-high-level_20.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-3753964665941381979"
tags: ["elasticsearch", "HighLevelRESTClient", "spring boot", "Tutorial"]
layout: post
---

![](https://i.imgur.com/wffZ6bK.png)

# 基於 Elasticsearch 搜尋商品 搜尋篇
踩坑中ing , 修改為 Java high-level REST client 連接 Elasticsearch

https://blog.csdn.net/u014646662/article/details/94718834
ElasticSearch 7.x 後續版本不支持指定索引
# 基於 docker install local ik zip
由於我的 windows 10 不支援 docker 懶得重灌 所以我用 docker tool
![](https://i.imgur.com/piQ7dIK.png)
可以看到這邊共享資料夾
重新新增 container
>
docker run --name es -p 9200:9200 -p 9300:9300 -e "discovery.type=single-node" -v /c/Users/test/:/data  -d docker.elastic.co/elasticsearch/elasticsearch:7.6.2
>
下在ik zip 至我們的  
>C:\Users\test
>
![](https://i.imgur.com/NXHCX3o.png)
>/usr/share/elasticsearch/bin/elasticsearch-plugin  install file:///data/elasticsearch-analysis-ik-7.6.2.zip
>
本地安裝 docker 之後exit docker restart es 重啟完成就可以使用我們的 ik 對 中文進行分詞了
![](https://i.imgur.com/ojznjvB.png)

後面對昨天的功能進行改版一下 後續改版 已經不支持索引 預設為 _doc 所以 發現這部分資料還是比較少的我們來補足一下

# esController
```java
@Controller
@RequestMapping("/esProduct")
public class esitemConntroller {
	
		@Autowired
	    private esitemService esProductService;

		@RequestMapping(value = "/createIndexMapping", method = RequestMethod.GET)
	    @ResponseBody
	    public String createIndexMapping() {
			return  esProductService.createIndexwithMapping();
	    }
		
		@RequestMapping(value = "/checkIndexMapping/{index}", method = RequestMethod.GET)
	    @ResponseBody
	    public String checkIndexMapping(@PathVariable String index) {
			return  esProductService.checkIndexMapping(index);
	    }
		
		@RequestMapping(value = "/deleteIndex/{index}", method = RequestMethod.GET)
	    @ResponseBody
	    public String deleteIndex(@PathVariable String index) {
			return  esProductService.deleteIndex(index);
	    }
		// 新增  document
		@RequestMapping(value = "/createDocument/{index}/{type}/{id}/{key}/{value}/{key2}/{value2}", method = RequestMethod.GET)
	    @ResponseBody
	    public String createDocument(@PathVariable String index,@PathVariable String type,
	    		@PathVariable String id,@PathVariable String key,@PathVariable String value
	    		,@PathVariable String key2,@PathVariable String value2) {
			return  esProductService.createDocument(index, type, id, key, value, key2, value2);
	    }
		
		// 更新 document
		@RequestMapping(value = "/updateDocument/{index}/{type}/{id}/{key2}/{value2}", method = RequestMethod.GET)
	    @ResponseBody
	    public String updateDocument(@PathVariable String index,@PathVariable String type,
	    		@PathVariable String id,@PathVariable String key,@PathVariable String value
	    		,@PathVariable String key2,@PathVariable String value2) {
			return  esProductService.updateDocument(index, type, id, key, value, key2, value2);
	    }
		
	     // 批量新增 document
		@RequestMapping(value = "/bulkDocument", method = RequestMethod.GET)
	    @ResponseBody
	    public String bulkDocument() {
			return  esProductService.bulkDocument();
	    }
		// 刪除 document
		@RequestMapping(value = "/deleteDocument/{documentCount}", method = RequestMethod.GET)
	    @ResponseBody
	    public String deleteDocument(@PathVariable Integer documentCount) {
			return  esProductService.deleteDocument(documentCount);
	    }
		
        
        // 搜尋 Document 
		@RequestMapping(value = "/searchDocument/{index}/{key}/{value}", method = RequestMethod.GET)
	    @ResponseBody
	    public String searchDocument(@PathVariable String index,@PathVariable String key,@PathVariable String value) {
			return  esProductService.searchDocument(index, key, value);
	    }
		
```

# Serverimpl
```java

@Service

public final class esitemServiceimpl implements esitemService {
	
	private static final String HOST = "192.168.99.100";
    // Elasticsearch查询服务器使用9200端口，我们可以通过RESTful API直接查询数据库。
    private static final int PORT_ONE = 9200;
    // REST服务器使用9201端口，外部客户端可以使用它来连接和执行操作。
    private static final int PORT_TWO = 9201;
    // 通信方式
    private static final String SCHEME = "http";
    // 高级客户端实例
    private static RestHighLevelClient restHighLevelClient;
    // Jackson 的转换类
    private static ObjectMapper objectMapper = new ObjectMapper();
    // 索引名称
    private static final String INDEX = "persondata";
    // 索引类型
    private static final String TYPE = "person";
  
    public esitemServiceimpl() {
    	super();
    	makeConnection();
    	
    }
    private static synchronized RestHighLevelClient makeConnection() {

        if(restHighLevelClient == null) {
            restHighLevelClient = new RestHighLevelClient(
                    RestClient.builder(
                            new HttpHost(HOST, PORT_ONE, SCHEME),
                            new HttpHost(HOST, PORT_TWO, SCHEME)));
        }
        System.out.println("RestHighLevelClient initialization successful!"); 
        return restHighLevelClient;
    }
    private static synchronized void closeConnection() throws IOException {
        restHighLevelClient.close();
        restHighLevelClient = null;
    } 
    
    
    @Override
    public  Person insertPerson(Person person){
    	
        person.setPersonId(UUID.randomUUID().toString());
        Map<String, Object> dataMap = new HashMap<String, Object>();
        dataMap.put("personId", person.getPersonId());
        dataMap.put("name", person.getName());
        IndexRequest indexRequest = new IndexRequest(INDEX, TYPE, person.getPersonId())
                .source(dataMap);
        try {
            IndexResponse response = restHighLevelClient.index(indexRequest,  RequestOptions.DEFAULT);
        } catch(ElasticsearchException e) {
            e.getDetailedMessage();
        } catch (java.io.IOException ex){
            ex.getLocalizedMessage();
        }
        return person;
    }
    @Override
    public   Person getPersonById(String id){
        GetRequest getPersonRequest = new GetRequest(INDEX, TYPE, id);
        GetResponse getResponse = null;
        try {
            getResponse = restHighLevelClient.get(getPersonRequest, RequestOptions.DEFAULT);
        } catch (java.io.IOException e){
            e.getLocalizedMessage();
        }
        return getResponse != null ?
                objectMapper.convertValue(getResponse.getSourceAsMap(), Person.class) : null;
    }
    @Override
    public Person updatePersonById(String id, Person person){
        UpdateRequest updateRequest = new UpdateRequest(INDEX, TYPE, id)
                .fetchSource(true);    // 更新后获取对象
        try {
            String personJson = objectMapper.writeValueAsString(person);
            updateRequest.doc(personJson, XContentType.JSON);
            UpdateResponse updateResponse = restHighLevelClient.update(updateRequest,  RequestOptions.DEFAULT);
            return objectMapper.convertValue(updateResponse.getGetResult().sourceAsMap(), Person.class);
        }catch (JsonProcessingException e){
            e.getMessage();
        } catch (java.io.IOException e){
            e.getLocalizedMessage();
        }
        System.out.println("Unable to update person");
        return null;
    }
    @Override
    public void deletePersonById(String id) {
        DeleteRequest deleteRequest = new DeleteRequest(INDEX, TYPE, id);
        try {
            DeleteResponse deleteResponse = restHighLevelClient.delete(deleteRequest,  RequestOptions.DEFAULT);
        } catch (java.io.IOException e){
            e.getLocalizedMessage();
        }
    }
	@Override
	public String createIndexwithMapping()  {
		// TODO Auto-generated method stub
		String result="";
		
		try {
			  CreateIndexRequest request = new CreateIndexRequest("pybbs");
			  request.settings(Settings.builder()
			      .put("index.number_of_shards", 1)
			      .put("index.number_of_shards", 5));

			  XContentBuilder mappingBuilder = JsonXContent.contentBuilder()
			      .startObject()
			        .startObject("properties")
				 
			         
			          .startObject("title")
			            .field("type", "text")
			            .field("analyzer", "ik_smart") //ik_smart
			            .field("index", "true")
			          .endObject()
			          .startObject("content")
			            .field("type", "text")
			            .field("analyzer", "ik_max_word") // ik_max_word 这个分词器是ik的，可以去github上搜索安装es的ik分词器插件
			            .field("index", "true")
			          .endObject()
			        .endObject()
			      .endObject();
			  request.mapping(mappingBuilder);

			  CreateIndexResponse response;
			response = restHighLevelClient.indices().create(request, RequestOptions.DEFAULT);
			System.out.println(response.isAcknowledged());
			  System.out.println(response.toString());
			  result =response.toString();
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}

		  
		  return result;
	}

	@Override
	public String checkIndexMapping(String Index) {
		String result="";
		  GetIndexRequest request = new GetIndexRequest();
		  request.indices(Index);
		  request.local(false);
		  request.humanReadable(true);

		  boolean exists;
		try {
			exists = restHighLevelClient.indices().exists(request, RequestOptions.DEFAULT);

			  result = ("result: {"+ exists + "}");
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}

		// TODO Auto-generated method stub
		return result;
	}
	@Override
	public String deleteIndex(String index) {
		String result="";
		 DeleteIndexRequest request = new DeleteIndexRequest(index);
		  request.indicesOptions(IndicesOptions.LENIENT_EXPAND_OPEN);

		  AcknowledgedResponse response;
		try {
			response = restHighLevelClient.indices().delete(request, RequestOptions.DEFAULT);
			result = "result: {"+response.isAcknowledged()+"}";
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}

		  
		// TODO Auto-generated method stub
		return result;
	}
	@Override
	public String createDocument(String index, String type , String id , String key ,String value, String key2 ,String value2) {
		String result="";

		  Map<String, Object> map = new HashMap<>();
		  map.put(key, value);
		  map.put(key2, value2);

		  IndexRequest request = new IndexRequest(index, type, id); // 这里最后一个参数是es里储存的id，如果不填，es会自动生成一个，个人建议跟自己的数据库表里id保持一致，后面更新删除都会很方便
		  request.source(map);
		  try {
			IndexResponse response = restHighLevelClient.index(request, RequestOptions.DEFAULT);
			result = "result: code: {"+response.status().getStatus()+"}, status: {"+response.status().name()+"}";
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		  

	        
		  // not exist: result: code: 201, status: CREATED
		  // exist: result: code: 200, status: OK
		  
		// TODO Auto-generated method stub
		return result;
	}
	@Override
	public String updateDocument(String index, String type , String id , String key ,String value, String key2 ,String value2) {
		String result="";
		  UpdateRequest request = new UpdateRequest(index, type, id);
		  Map<String, Object> map = new HashMap<>();
		  map.put(key, value);
		  map.put(key2, value2);
		  request.doc(map);

		  try {
			UpdateResponse response = restHighLevelClient.update(request, RequestOptions.DEFAULT);
			result ="result: code: {"+response.status().getStatus()+"}, status: {"+response.status().name()+"}"; 
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		// TODO Auto-generated method stub
		return result;
	}
	@Override
	public String bulkDocument() {
		String result="";

		  BulkRequest requests = new BulkRequest();

		  Map<String, Object> map1 = new HashMap<>();
		  map1.put("title", "我是台灣人 ,im taiwan");
		  IndexRequest request1 = new IndexRequest("pybbs", "_doc", "1");
		  request1.source(map1);
		  requests.add(request1);

		  Map<String, Object> map2 = new HashMap<>();
		  map2.put("title", "高雄市安安");
		  IndexRequest request2 = new IndexRequest("pybbs", "_doc", "2");
		  request2.source(map2);
		  requests.add(request2);

		  Map<String, Object> map3 = new HashMap<>();
		  map3.put("title", "台北安安");
		  IndexRequest request3 = new IndexRequest("pybbs", "_doc", "3");
		  request3.source(map3);
		  requests.add(request3);

		  try {
			BulkResponse responses = restHighLevelClient.bulk(requests, RequestOptions.DEFAULT);
			result ="result: code: {"+responses.status().getStatus()+"}, status: {"+ responses.status().name()+"}";
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		  // not exist: result: code: 200, status: OK
		  // exist: result: code: 200, status: OK
		  
		  
		// TODO Auto-generated method stub
		return result;
	}
	@Override
	public String deleteDocument(Integer documentCount) {
		String result="";

		  for (int i = 1; i <= documentCount; i++) {
		    DeleteRequest request = new DeleteRequest("pybbs", "_doc", String.valueOf(i));

		    try {
				DeleteResponse response = restHighLevelClient.delete(request, RequestOptions.DEFAULT);
				System.out.println("result: code: {"+response.status().getStatus()+"}, status: {"+response.status().name()+"}");
				result = "result: code: {"+response.status().getStatus()+"}, status: {"+response.status().name()+"}";
			} catch (IOException e) {
				
				// TODO Auto-generated catch block
				e.printStackTrace();
				return e.toString();
			}
		    // exist: result: code: 200, status: OK
		    // not exist: result: code: 404, status: NOT_FOUND
		    
//		    log.info("result: code: {}, status: {}", response.status().getStatus(), response.status().name());
		  }
		// TODO Auto-generated method stub
		return result;
	}
	@Override
	public String searchDocument(String index ,String key , String value) {
		String result="";

		  SearchRequest request = new SearchRequest(index);
		  SearchSourceBuilder builder = new SearchSourceBuilder();
		  builder.query(QueryBuilders.matchQuery(key, value));
		
		  // builder.from(0).size(2); // 分頁
		  request.source(builder);

		  SearchResponse response;
		try {
			response = restHighLevelClient.search(request, RequestOptions.DEFAULT);
			  System.out.println(response.toString() + "\n"+response.getTotalShards());
			  for (SearchHit documentFields : response.getHits()) {
				String tmp ="result: {"+ documentFields.toString()+"}, code: {"+response.status().getStatus()+"}, status: {"+response.status().name()+"}\n";
			    System.out.println(tmp);
			    result = result += tmp;
			  }
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
			return e.toString();
		}
//		  log.info(response.toString(), response.getTotalShards());
	
		// TODO Auto-generated method stub
		return result;
	}

}

```

# service
```java

public interface esitemService {
  
    
    String createIndexwithMapping() ;
    
    String checkIndexMapping(String Index);
    
    String deleteIndex(String Index);
    
    String createDocument(String index, String type , String id , String key ,String value , String key2 ,String value2);
    
    String updateDocument(String index, String type , String id , String key ,String value, String key2 ,String value2);
    
    String bulkDocument();
    
    String deleteDocument(Integer documentCount);
    
    String searchDocument(String index ,String key , String value);
}
```

來演示一下

# 創建mapping
![](https://i.imgur.com/BURZmmm.png)
http://localhost:8080/esProduct/createIndexMapping

```java
	@Override
	public String createIndexwithMapping()  {
		// TODO Auto-generated method stub
		String result="";
		
		try {
			  CreateIndexRequest request = new CreateIndexRequest("pybbs");
			  request.settings(Settings.builder()
			      .put("index.number_of_shards", 1)
			      .put("index.number_of_shards", 5));

			  XContentBuilder mappingBuilder = JsonXContent.contentBuilder()
			      .startObject()
			        .startObject("properties")
				 
			         
			          .startObject("title")
			            .field("type", "text")
			            .field("analyzer", "ik_smart") //ik_smart
			            .field("index", "true")
			          .endObject()
			          .startObject("content")
			            .field("type", "text")
			            .field("analyzer", "ik_max_word") // ik_max_word 这个分词器是ik的，可以去github上搜索安装es的ik分词器插件
			            .field("index", "true")
			          .endObject()
			        .endObject()
			      .endObject();
			  request.mapping(mappingBuilder);

			  CreateIndexResponse response;
			response = restHighLevelClient.indices().create(request, RequestOptions.DEFAULT);
			System.out.println(response.isAcknowledged());
			  System.out.println(response.toString());
			  result =response.toString();
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}

		  
		  return result;
	}
```

# 檢查 mapping
http://localhost:8080/esProduct/checkIndexMapping/pybbs
![](https://i.imgur.com/c4GeeFb.png)

```java
	@Override
	public String checkIndexMapping(String Index) {
		String result="";
		  GetIndexRequest request = new GetIndexRequest();
		  request.indices(Index);
		  request.local(false);
		  request.humanReadable(true);

		  boolean exists;
		try {
			exists = restHighLevelClient.indices().exists(request, RequestOptions.DEFAULT);

			  result = ("result: {"+ exists + "}");
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}

		// TODO Auto-generated method stub
		return result;
	}
```

# 刪除 index
http://localhost:8080/esProduct/deleteIndex/pybbs
![](https://i.imgur.com/8G48hRJ.png)

```java
	@Override
	public String deleteIndex(String index) {
		String result="";
		 DeleteIndexRequest request = new DeleteIndexRequest(index);
		  request.indicesOptions(IndicesOptions.LENIENT_EXPAND_OPEN);

		  AcknowledgedResponse response;
		try {
			response = restHighLevelClient.indices().delete(request, RequestOptions.DEFAULT);
			result = "result: {"+response.isAcknowledged()+"}";
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}

		  
		// TODO Auto-generated method stub
		return result;
	}
```

# 新增 documet
http://localhost:8080/esProduct/createDocument/pybbs/_doc/2/title/%E5%8F%B0%E7%81%A3%E4%BD%A0%E5%A5%BD/content/%E5%8F%B0%E5%8C%97

![](https://i.imgur.com/OhoL1qx.png)

http://localhost:8080/esProduct/createDocument/pybbs/_doc/2/title/%E9%A6%99%E6%B8%AF%E4%BD%A0%E5%A5%BD/content/%E5%9C%8B%E5%AE%B6
![](https://i.imgur.com/UNioTQN.png)

![](https://i.imgur.com/YlMy9Ll.png)

```java

	@Override
	public String createDocument(String index, String type , String id , String key ,String value, String key2 ,String value2) {
		String result="";

		  Map<String, Object> map = new HashMap<>();
		  map.put(key, value);
		  map.put(key2, value2);

		  IndexRequest request = new IndexRequest(index, type, id); // 这里最后一个参数是es里储存的id，如果不填，es会自动生成一个，个人建议跟自己的数据库表里id保持一致，后面更新删除都会很方便
		  request.source(map);
		  try {
			IndexResponse response = restHighLevelClient.index(request, RequestOptions.DEFAULT);
			result = "result: code: {"+response.status().getStatus()+"}, status: {"+response.status().name()+"}";
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		  

	        
		  // not exist: result: code: 201, status: CREATED
		  // exist: result: code: 200, status: OK
		  
		// TODO Auto-generated method stub
		return result;
	}
```
# 更新 document
http://localhost:8080/esProduct/updateDocument/pybbs/_doc/2/title/%E9%A6%99%E6%B8%AF%E4%BD%A0%E5%A5%BD/content/%E6%97%BA%E8%A7%92
![](https://i.imgur.com/8ltrZWW.png)

![](https://i.imgur.com/wlsoa6o.png)

```
	@Override
	public String updateDocument(String index, String type , String id , String key ,String value, String key2 ,String value2) {
		String result="";
		  UpdateRequest request = new UpdateRequest(index, type, id);
		  Map<String, Object> map = new HashMap<>();
		  map.put(key, value);
		  map.put(key2, value2);
		  request.doc(map);

		  try {
			UpdateResponse response = restHighLevelClient.update(request, RequestOptions.DEFAULT);
			result ="result: code: {"+response.status().getStatus()+"}, status: {"+response.status().name()+"}"; 
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		// TODO Auto-generated method stub
		return result;
	}
```
# 批量新增 document
http://localhost:8080/esProduct/bulkDocument
![](https://i.imgur.com/mi7VNNy.png)
![](https://i.imgur.com/XaLTrWm.png)

```java
	@Override
	public String bulkDocument() {
		String result="";

		  BulkRequest requests = new BulkRequest();

		  Map<String, Object> map1 = new HashMap<>();
		  map1.put("title", "我是台灣人 ,im taiwan");
		  IndexRequest request1 = new IndexRequest("pybbs", "_doc", "1");
		  request1.source(map1);
		  requests.add(request1);

		  Map<String, Object> map2 = new HashMap<>();
		  map2.put("title", "高雄市安安");
		  IndexRequest request2 = new IndexRequest("pybbs", "_doc", "2");
		  request2.source(map2);
		  requests.add(request2);

		  Map<String, Object> map3 = new HashMap<>();
		  map3.put("title", "台北安安");
		  IndexRequest request3 = new IndexRequest("pybbs", "_doc", "3");
		  request3.source(map3);
		  requests.add(request3);

		  try {
			BulkResponse responses = restHighLevelClient.bulk(requests, RequestOptions.DEFAULT);
			result ="result: code: {"+responses.status().getStatus()+"}, status: {"+ responses.status().name()+"}";
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		  // not exist: result: code: 200, status: OK
		  // exist: result: code: 200, status: OK
		  
		  
		// TODO Auto-generated method stub
		return result;
	}
```

# 刪除 document
http://localhost:8080/esProduct/deleteDocument/3
![](https://i.imgur.com/MzSgtDX.png)
![](https://i.imgur.com/QGakZoR.png)

```java
	@Override
	public String deleteDocument(Integer documentCount) {
		String result="";

		  for (int i = 1; i <= documentCount; i++) {
		    DeleteRequest request = new DeleteRequest("pybbs", "_doc", String.valueOf(i));

		    try {
				DeleteResponse response = restHighLevelClient.delete(request, RequestOptions.DEFAULT);
				System.out.println("result: code: {"+response.status().getStatus()+"}, status: {"+response.status().name()+"}");
				result = "result: code: {"+response.status().getStatus()+"}, status: {"+response.status().name()+"}";
			} catch (IOException e) {
				
				// TODO Auto-generated catch block
				e.printStackTrace();
				return e.toString();
			}
		    // exist: result: code: 200, status: OK
		    // not exist: result: code: 404, status: NOT_FOUND
		    
//		    log.info("result: code: {}, status: {}", response.status().getStatus(), response.status().name());
		  }
		// TODO Auto-generated method stub
		return result;
	}
```

# 搜尋 document
http://localhost:8080/esProduct/searchDocument/pybbs/title/%E5%8F%B0%E7%81%A3
![](https://i.imgur.com/bf5VJOY.png)
http://localhost:8080/esProduct/searchDocument/pybbs/title/%E9%A6%99%E6%B8%AF
![](https://i.imgur.com/Orz7DRD.png)
http://localhost:8080/esProduct/searchDocument/pybbs/title/%E4%BD%A0%E5%A5%BD
![](https://i.imgur.com/Kth0kew.png)
```java
	@Override
	public String searchDocument(String index ,String key , String value) {
		String result="";

		  SearchRequest request = new SearchRequest(index);
		  SearchSourceBuilder builder = new SearchSourceBuilder();
		  builder.query(QueryBuilders.matchQuery(key, value));
		
		  // builder.from(0).size(2); // 分頁
		  request.source(builder);

		  SearchResponse response;
		try {
			response = restHighLevelClient.search(request, RequestOptions.DEFAULT);
			  System.out.println(response.toString() + "\n"+response.getTotalShards());
			  for (SearchHit documentFields : response.getHits()) {
				String tmp ="result: {"+ documentFields.toString()+"}, code: {"+response.status().getStatus()+"}, status: {"+response.status().name()+"}\n";
			    System.out.println(tmp);
			    result = result += tmp;
			  }
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
			return e.toString();
		}
//		  log.info(response.toString(), response.getTotalShards());
	
		// TODO Auto-generated method stub
		return result;
	}
```

