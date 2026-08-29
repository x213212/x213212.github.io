---
title: "Spring 基於 Elasticsearch 搜尋商品 (三) 使用 Java High Level REST Client 連接 es 完成 crud"
date: "2020-05-18T12:11:00.001+08:00"
updated: "2020-07-07T07:35:38.941+08:00"
permalink: "/2020/05/spring-elasticsearch-java-high-level.html"
original_url: "https://x8795278.blogspot.com/2020/05/spring-elasticsearch-java-high-level.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-7627500904845459652"
tags: ["elasticsearch", "HighLevelRESTClient", "spring boot", "Tutorial"]
layout: post
---

![](https://i.imgur.com/wffZ6bK.png)

# 基於 Elasticsearch 搜尋商品 連接篇
踩坑中ing , 修改為 Java high-level REST client 連接 Elasticsearch

# entity
```java
public class Person {
    private String personId;
    private String name;

    // 省略setter,getter

    @Override
    public String toString() {
        return "Person{" +
                "personId='" + personId + '\'' +
                ", name='" + name + '\'' +
                '}';
    }

	public String getPersonId() {
		return personId;
	}

	public void setPersonId(String personId) {
		this.personId = personId;
	}

	public String getName() {
		return name;
	}

	public void setName(String name) {
		this.name = name;
	}
}
```
# esController
```java
@Controller
@RequestMapping("/esProduct")
public class esitemConntroller {
	
		@Autowired
	    private esitemService esProductService;

		@RequestMapping(value = "/newindex/{personId}/{name}", method = RequestMethod.GET)
	    @ResponseBody
	    public String newindex(@PathVariable String personId,@PathVariable String name) {
			System.out.println("Inserting a new Person with name xiaoyaook...");
	        Person person = new Person();
	        person.setName(name);
	        //person.setPersonId(personId);
	        person = esProductService.insertPerson(person);
	        System.out.println("Person inserted --> " + person);
			return "Person inserted --> " + person;
	    }
		   

		@RequestMapping(value = "/updateindex/{personId}/{name}", method = RequestMethod.GET)
	    @ResponseBody
	    public String updateindex(@PathVariable String personId,@PathVariable String name) {
	        System.out.println("Changing name to `XY`...");
	        Person person = new Person();
	        Person personFromDB = esProductService.getPersonById(personId);
	        person.setName(name);
	        person.setPersonId(personFromDB.getPersonId());
	        esProductService.updatePersonById(personId, person);
	        

			return "Person updated  --> " + person;
	    }
		
		
		@RequestMapping(value = "/getindex/{id}", method = RequestMethod.GET)
	    @ResponseBody
	    public String getindex(@PathVariable String id) {
	        System.out.println("Getting XY...");
	        Person personFromDB = esProductService.getPersonById(id);
	        System.out.println("Person from DB  --> " + personFromDB);
			return "Person from DB  --> " + personFromDB;
	    }
		
		@RequestMapping(value = "/deleteindex/{personId}", method = RequestMethod.GET)
	    @ResponseBody
	    public String deleteindex(@PathVariable String personId) {

	        System.out.println("Deleting XY...");
	        //Person personFromDB = esProductService.getPersonById(id);
	        esProductService.deletePersonById(personId);
//	        System.out.println("Person from DB  --> " + personFromDB);
			return "Person Deleted";
	    }
		
		
```

# esService
```java
/**
 * 
 * @author x2132
 * 商品搜尋管理 service
 * 2020/5/16
 *
 */

public interface esitemService {
    /**
     * 新增到ES
     */
	Person insertPerson(Person person);

    /**
     * 根據 id 取得商品
     */
    Person getPersonById(String id);

    /**
     * 根據id 更新商品
     * @return 
     */
    Person  updatePersonById(String id, Person person);

    /**
     * 根據id 刪除商品
     */
    void deletePersonById(String id);

}
```
# esitemServiceimpl
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
	

}

```

# newindex
預設 person 在 esitemServiceimpl 產生uuid 編號
http://localhost:8080/esProduct/newindex/1/test
![](https://i.imgur.com/RXjvqKk.png)

![](https://i.imgur.com/l8YPiF8.png)

# updateindex
http://localhost:8080/esProduct/updateindex/032d4288-a7bd-44f0-a875-b89ea6cda80c/hah214
![](https://i.imgur.com/XA8B3xK.png)
異動版本號會更新
![](https://i.imgur.com/QBlqaZJ.png)

# getindex
http://localhost:8080/esProduct/getindex/6929b00d-c7f0-46c4-b0d8-ab6b9f610456
![](https://i.imgur.com/qTi0wfy.png)

# deleteindex
http://localhost:8080/esProduct/deleteindex/032d4288-a7bd-44f0-a875-b89ea6cda80c
![](https://i.imgur.com/5ZeNQL2.png)
刪除032d4288-a7bd-44f0-a875-b89ea6cda80c
![](https://i.imgur.com/jMUA1hb.png)

後續會補足 全文搜尋 匹配搜尋 等等 還有搭配我們的 kibana 顯示搜尋分析 最後就是透過我們的 logstash 同步mysql或者是 kafaka 同步我們的數據到我們的 es

