---
title: ".net entity framework 初步探討 (三) Code first"
date: "2019-12-05T11:02:00.001+08:00"
updated: "2019-12-05T12:14:51.111+08:00"
permalink: "/2019/12/net-entity-framework-code-first.html"
original_url: "https://x8795278.blogspot.com/2019/12/net-entity-framework-code-first.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-2031017131446026894"
tags: [".NET", "C#", "Tutorial"]
layout: post
---

有點猶豫這個要放在 第一個 還是 第二個 xd
# 建立一個 [ADO.NET](http://ado.net/) 資料庫模型

![](https://i.imgur.com/lueORAn.png)

  

選用 ADO.NET實體資料庫模型  

![](https://i.imgur.com/MOe7l25.png)

# Code generate db

產生一個資料庫並連接
```
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Data.Entity;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;
using System.Data.Entity.Infrastructure;

namespace WindowsFormsApp1
{
    public class BlogContext : DbContext
    {
        public DbSet<Blog> Blogs { get; set; }
    }

    public class Blog
    {
        public int BlogId { get; set; }
        public string Name { get; set; }
    }
}
```
```
using (var db = new BlogContext())
            {
                // Create and save a new Blog
                Console.Write("Enter a name for a new Blog: ");
                var name = Console.ReadLine();

                var blog = new Blog { Name = name };
                db.Blogs.Add(blog);
                db.SaveChanges();
            }
```
以現有資料庫去連接
```
class video
    {
        [Key]
        public string title { get; set; }
        public string dec  { get; set; }
        public string dec2 { get; set; }
        public string dec3 { get; set; }
    }
    class MeContext : DbContext
    {
        public MeContext() : base(@"Data Source=(localdb)\MSSQLLocalDB;Initial Catalog=WindowsFormsApp1.BlogContext;Integrated Security=True;") { }
        public DbSet<video> videos { get;set;}

    }
```
```
using (var db = new MeContext()) 引用
            {
                String timeStamp = GetTimestamp(DateTime.Now);
                db.videos.Add(new video { title = timeStamp, dec ="test",dec2 ="123", dec3 = "123" });
                db.SaveChanges();

            }
```
# Code first from db

![](https://i.imgur.com/rDMtX7G.png)

  

![](https://i.imgur.com/lNraCxB.png)

  

按下後即可以產生相對應 code，這邊當然不只有 MSSQL 如果你要用 mysql 可以去 Nuget 去下載相對應的套件  

![](https://i.imgur.com/j0ZZZxO.png)

  

這邊就是我們剛剛編寫的sql  

![](https://i.imgur.com/dQt22Gd.png)

  

那麼引用的方法就是，可能會遇到 video找不到的問題  

![](https://i.imgur.com/ckNkqtW.png)

  

他自動產生可能會多加一個s 可以在這邊進行修改  

![](https://i.imgur.com/MQiKQYp.png)

```
using (var db = new Model1())
            {
                String timeStamp = GetTimestamp(DateTime.Now);
                db.videos.Add(new video { title = timeStamp, dec = "test", dec2 = "123", dec3 = "123" });
                db.SaveChanges();
                // Display all Blogs from the database
                var query = from b in db.videos
                            orderby b.title
                            select b;

                Console.WriteLine("All blogs in the database:");
                foreach (var item in query)
                {
                    Console.WriteLine(item.title);
                }

            }
```
# Model 的 base

![](https://i.imgur.com/Xi8C4R2.png)

  

![](https://i.imgur.com/4uekwEB.png)

還記得前面幾系列的開頭嗎 不是有一個新增到App.config  

這邊也可以進行修改
# 欄位發生異動

<https://dotblogs.com.tw/skychang/archive/2012/04/04/71276.aspx>
這篇文章講得很清楚
在　Package Manager Console　　而不是在　一般的　console  

Enable-Migrations
Add-Migration "AddEName"
Update-Database
範例
當 我的資料庫裡面沒有 videos 的table 的話或者 我們進行異動欄位，我們就可以透過這方法，不用重新砍掉資料庫而直接新增欄位重建等等

![](https://i.imgur.com/cCOjowH.png)
