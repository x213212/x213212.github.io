---
title: "Vue element admin Table 替換 資料(三)"
date: "2019-06-03T10:58:00.003+08:00"
updated: "2019-06-22T20:02:34.198+08:00"
permalink: "/2019/06/vue-element-admin-table.html"
original_url: "https://x8795278.blogspot.com/2019/06/vue-element-admin-table.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-9109301748231384364"
tags: ["spring boot", "Tutorial", "Vue.js"]
layout: post
---

# Java object to json 小轉換

# <https://blog.csdn.net/qq_37525899/article/details/81132069> 在不破壞結構的狀態下 進行後端移植table 觀察官方 預設返回的結構後 ![](https://i.imgur.com/S00Ojwx.png) 需要注意一點，在 List 的 變數 需要 在 初始化 的時候指定為 ``` new ArrayList<>() ``` <https://stackoverflow.com/questions/43705582/java-lang-unsupportedoperationexception-adding-to-a-list> 然後 就是 編寫 java object to json 的寫法 ``` http://localhost:9990/httpMethod2 ``` ![](https://i.imgur.com/CfMgGe7.png) ![](https://i.imgur.com/qt7c8EZ.png) ![](https://i.imgur.com/NOx4e6c.png) 收工， 接下來要詳細針對 個別控件 透過 vue routuer 進行傳值的詳細分析，預計大概五天

**`list.java`**

```java
package com.model;

import java.awt.print.Book;
import java.util.ArrayList;

import org.springframework.beans.factory.annotation.Autowired;

public class List {

	@Autowired private Integer code;
	@Autowired private ListData data;

    public List(){
    	code = 0;

    }

    public List(Integer code, String data,String name,String[] tmp) {
        super();
        this.code = code;

    }

    public Integer getCode() {
        return code;
    }

    public void setCode(Integer code) {
        this.code = code;
    }

 
	public ListData getData() {
		return data;
	}
	public void setData(ListData data) {
		this.data = data;
		this.data.coutTotlal();
		
	}
}
```

**`listdata`**

```
package com.model;

import java.util.ArrayList;
import java.util.List;

import org.springframework.beans.factory.annotation.Autowired;
public class ListData {
	
	@Autowired private Integer total;
	@Autowired private List<ListItem> items;
    
//	private List<Author> author = new ArrayList<Author>();

    public void ListData (Integer total,List<ListItem> items){
    	this.total = total;
    	this.items = items;
    }
    public Integer gettotal(){
    	return  total;
    }
    public List<ListItem> getitems()
    {
    	return items;
    	
    }
    public void addList (ListItem tmp)
    {
    	this.items.add(tmp);
    }
    public void  coutTotlal()
    {
    	this.total = items.size();
    	
    }
	
    public ListData(){
    	this.total = 0;
    	this.items =new ArrayList<>();
    }


	
//	public List<Author> getAuthor() {
//		return author;
//	}
//	public void setAuthor(List<Author> author) {
//		this.author = author;
//	}

}
```

**`listitem`**

```
package com.model;

import org.springframework.beans.factory.annotation.Autowired;

public class ListItem {
	
	@Autowired  private Integer id;
	@Autowired private String title ;
	@Autowired private String status ; 
	@Autowired private String author; 
	@Autowired private String displaytime ;
	@Autowired  private String pagviews ;
    

    
//	private List<Author> author = new ArrayList<Author>();

    public void setid (Integer id){
    	this.id = id;
    }
    public Integer getid(){
    	return  id;
    }

    public void settitle(String token){
    	this.title = token;
    }
    public String gettitle(){
    	return  title;
    }
    public void setstatus(String status){
    	this.status = status;
    }
    public String getstatus(){
    	return  status;
    }
    public void setauthor(String author){
    	this.author= author;
    }
    public String getauthor(){
    	return  author;
    }
    public void setdisplaytime(String displaytime){
    	this.displaytime = displaytime;
    }
    public String getdisplaytime(){
    	return  displaytime;
    }
    public void setpagviews (String pagviews){
    	this.pagviews = pagviews;
    }
    public String gettoken(){
    	return  pagviews;
    }
	public void show_data ()
	{
		System.out.println(this.id + this.title);
		
	}
    public ListItem(){

    }


	
//	public List<Author> getAuthor() {
//		return author;
//	}
//	public void setAuthor(List<Author> author) {
//		this.author = author;
//	}

}
```

**`me.json`**

```json
{
    "code": 20000, 
    "data": {
        "total": 10, 
        "items": [
            {
                "id": 0, 
                "title": "test0", 
                "status": "false", 
                "author": "null", 
                "displaytime": "null", 
                "token": "null"
            }, 
            {
                "id": 1, 
                "title": "test1", 
                "status": "false", 
                "author": "null", 
                "displaytime": "null", 
                "token": "null"
            }, 
            {
                "id": 2, 
                "title": "test2", 
                "status": "false", 
                "author": "null", 
                "displaytime": "null", 
                "token": "null"
            }, 
            {
                "id": 3, 
                "title": "test3", 
                "status": "false", 
                "author": "null", 
                "displaytime": "null", 
                "token": "null"
            }, 
            {
                "id": 4, 
                "title": "test4", 
                "status": "false", 
                "author": "null", 
                "displaytime": "null", 
                "token": "null"
            }, 
            {
                "id": 5, 
                "title": "test5", 
                "status": "false", 
                "author": "null", 
                "displaytime": "null", 
                "token": "null"
            }, 
            {
                "id": 6, 
                "title": "test6", 
                "status": "false", 
                "author": "null", 
                "displaytime": "null", 
                "token": "null"
            }, 
            {
                "id": 7, 
                "title": "test7", 
                "status": "false", 
                "author": "null", 
                "displaytime": "null", 
                "token": "null"
            }, 
            {
                "id": 8, 
                "title": "test8", 
                "status": "false", 
                "author": "null", 
                "displaytime": "null", 
                "token": "null"
            }, 
            {
                "id": 9, 
                "title": "test9", 
                "status": "false", 
                "author": "null", 
                "displaytime": "null", 
                "token": "null"
            }
        ]
    }
}
```

**`mock.json`**

```json
{
	"code": 20000,
	"data": {
		"total": 30,
		"items": [{
			"id": "220000200007265819",
			"title": "Lndzx gxdmqtdh promfdx wteacqjmj ojvhyoqd nlykh.",
			"status": "draft",
			"author": "name",
			"display_time": "2018-07-21 11:39:16",
			"pageviews": 619
		}, {
			"id": "820000199705196765",
			"title": "Pgznkelkrd dorrlt gsbjzmjwk ajmn oqf.",
			"status": "draft",
			"author": "name",
			"display_time": "1973-09-04 16:33:27",
			"pageviews": 482
		}, {
			"id": "420000201302044930",
			"title": "Ofih lqrqjulc efkp spexx ltby ebst yonsivoch louhpr lowxqgvbn.",
			"status": "published",
			"author": "name",
			"display_time": "2014-09-15 04:04:53",
			"pageviews": 3854
		}, {
			"id": "820000197501296730",
			"title": "Ftvkefhc jvrjviuc.",
			"status": "draft",
			"author": "name",
			"display_time": "2001-06-05 18:24:16",
			"pageviews": 2946
		}, {
			"id": "510000199909043047",
			"title": "Vjnf litww qgqjgd.",
			"status": "draft",
			"author": "name",
			"display_time": "2018-10-21 01:24:55",
			"pageviews": 2466
		}, {
			"id": "36000019911003925X",
			"title": "Xmonkk ucofew fxp geip lyt.",
			"status": "draft",
			"author": "name",
			"display_time": "1987-01-16 06:58:51",
			"pageviews": 3630
		}, {
			"id": "220000200305151887",
			"title": "Red scddl jvcmrg hlhjp hck nzqrkvwpj mjggv rqkecwhup.",
			"status": "draft",
			"author": "name",
			"display_time": "2016-02-27 17:41:13",
			"pageviews": 842
		}, {
			"id": "990000197412243430",
			"title": "Iec rsugdy flo usganxbbl wsnb hlvj dvsqjmvvec.",
			"status": "published",
			"author": "name",
			"display_time": "1981-04-30 03:40:41",
			"pageviews": 3552
		}, {
			"id": "370000198409131242",
			"title": "Qfzsom mruszlpn fofr gcjixnkng uylmmkkle dyovwv iklrqrh qgq xkfwdm.",
			"status": "published",
			"author": "name",
			"display_time": "1972-03-25 09:13:25",
			"pageviews": 3971
		}, {
			"id": "530000200103311638",
			"title": "Iwlvc kmzgnhwmll.",
			"status": "published",
			"author": "name",
			"display_time": "2001-10-16 00:11:30",
			"pageviews": 1395
		}, {
			"id": "710000201203167651",
			"title": "Bxfoxrhqv bwbvdppkl ekgsehmgs wrigobajkj ppcxx.",
			"status": "deleted",
			"author": "name",
			"display_time": "1999-12-17 22:40:57",
			"pageviews": 3045
		}, {
			"id": "62000020170923643X",
			"title": "Qryahrovq xowvklgy wrweahesq siea jjced uevk bpiijrp bfstbnw.",
			"status": "draft",
			"author": "name",
			"display_time": "1971-11-16 12:00:10",
			"pageviews": 4049
		}, {
			"id": "450000199504158368",
			"title": "Csjobwjp nhls bvmpmnhn tuecbschl jjrpl gzznuo oueiy rbpays ivjupv.",
			"status": "draft",
			"author": "name",
			"display_time": "1991-09-29 00:41:29",
			"pageviews": 2774
		}, {
			"id": "610000201904166658",
			"title": "Dlfj fwhsfi fpfjo pokx ypbbscn.",
			"status": "published",
			"author": "name",
			"display_time": "1992-07-13 00:25:05",
			"pageviews": 3399
		}, {
			"id": "370000198802095348",
			"title": "Cgeyemi vuiu xmeufhwrs.",
			"status": "draft",
			"author": "name",
			"display_time": "1978-03-06 17:51:01",
			"pageviews": 3844
		}, {
			"id": "140000197501212064",
			"title": "Erkedfstl anmnss axxylqqvj egbn ckhbnxdn miioli lwtihei.",
			"status": "draft",
			"author": "name",
			"display_time": "2011-09-02 11:03:06",
			"pageviews": 3154
		}, {
			"id": "540000201112277247",
			"title": "Buhkm tdoy tsxsrlo.",
			"status": "draft",
			"author": "name",
			"display_time": "2008-01-23 03:22:22",
			"pageviews": 1676
		}, {
			"id": "510000199806261148",
			"title": "Nunbomrgtt rwlrfxq mcpfdtoo dudx ywfbzu qlyb kvqkazas leysqqx.",
			"status": "draft",
			"author": "name",
			"display_time": "1976-09-19 12:13:13",
			"pageviews": 2599
		}, {
			"id": "620000198409168717",
			"title": "Fkjlwm iscf ylhu zubz.",
			"status": "draft",
			"author": "name",
			"display_time": "1998-10-26 16:09:42",
			"pageviews": 2305
		}, {
			"id": "440000198509061171",
			"title": "Jbbfngyab sivorljqh qhdcqvuk jlmdtcq cxhhwbst btcqjzwhw vhckg xolcmhkgr uxuvgvic fdcoucsm.",
			"status": "deleted",
			"author": "name",
			"display_time": "2012-04-24 15:45:51",
			"pageviews": 1407
		}, {
			"id": "410000198204230864",
			"title": "Fipwnkqtc irdnkbyxbf imfkplgwlm fxjpqgfc bjbyqnv hchvl gicmevrwn.",
			"status": "draft",
			"author": "name",
			"display_time": "1994-03-09 09:41:48",
			"pageviews": 3091
		}, {
			"id": "710000200105032636",
			"title": "Votjqxtlb bkgyscp.",
			"status": "draft",
			"author": "name",
			"display_time": "2016-11-14 07:55:20",
			"pageviews": 4740
		}, {
			"id": "220000197509102724",
			"title": "Putodlfj tljbkdkbx vsq wdgwxrmcc aenori clnao jwmwfzu mlmnqde tgxn.",
			"status": "draft",
			"author": "name",
			"display_time": "1974-01-10 13:41:44",
			"pageviews": 4170
		}, {
			"id": "650000197904217089",
			"title": "Hppj nqkdds pncmc hlwiaurjr amdp alrxiljgkt.",
			"status": "published",
			"author": "name",
			"display_time": "2015-07-01 16:50:46",
			"pageviews": 3532
		}, {
			"id": "710000200501257714",
			"title": "Eymvtkz iywpm blxrgoey xvdlxrr wcvnu nmh jvwucc.",
			"status": "deleted",
			"author": "name",
			"display_time": "2009-09-15 18:31:39",
			"pageviews": 1035
		}, {
			"id": "320000201112272349",
			"title": "Nxlpvy ofkm uqmx gqdoakhd.",
			"status": "deleted",
			"author": "name",
			"display_time": "2013-11-09 03:51:23",
			"pageviews": 3120
		}, {
			"id": "710000199901148968",
			"title": "Iuhyq hwatxy myqujo.",
			"status": "deleted",
			"author": "name",
			"display_time": "1989-11-03 22:28:06",
			"pageviews": 1820
		}, {
			"id": "820000200001294215",
			"title": "Gshtjrecy tnohigg pjx nku.",
			"status": "draft",
			"author": "name",
			"display_time": "2010-11-21 12:38:12",
			"pageviews": 1980
		}, {
			"id": "440000199210243389",
			"title": "Enjemy djfhvdrq yejbswtch.",
			"status": "deleted",
			"author": "name",
			"display_time": "1973-07-21 03:54:09",
			"pageviews": 1832
		}, {
			"id": "120000197012251069",
			"title": "Rbh ljtljtol qgf bbgdizk.",
			"status": "draft",
			"author": "name",
			"display_time": "1983-01-18 00:13:50",
			"pageviews": 4415
		}]
	}
}
```

**`springboot.java`**

```java
@CrossOrigin
    @GetMapping("/httpMethod2")
	@ResponseBody

	public List httpMethod2() throws JsonProcessingException{
	List listest= new List();

	ListData item = new ListData ();
	
	listest.setCode(20000);
	

	for ( int i = 0 ; i < 10; i ++)
	{
		ListItem items = new ListItem ();
		items.setid(i);
		items.setstatus("false");
		items.settitle("test" + i);
		items.setauthor("null");
		items.setdisplaytime("null");
		items.setpagviews("null");
		items.show_data();
		/// add 陣列
		item.addList(items);
		//item.items.add(items);
	}
	listest.setData(item);
	
	ObjectMapper objectMapper = new ObjectMapper();
	
	String userJsonStr = objectMapper.writeValueAsString(listest);
	System.out.print(userJsonStr);
	return listest;
	}
	
```
