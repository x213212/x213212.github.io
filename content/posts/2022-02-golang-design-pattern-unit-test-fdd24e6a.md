---
title: "golang design pattern & unit test"
date: "2022-02-08T05:05:00.001+08:00"
updated: "2022-02-08T05:05:18.132+08:00"
permalink: "/2022/02/golang-design-pattern-unit-test.html"
original_url: "https://x8795278.blogspot.com/2022/02/golang-design-pattern-unit-test.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-5667361481945045896"
tags: ["Go"]
layout: post
---

![](https://upload.wikimedia.org/wikipedia/commons/thumb/0/05/Go_Logo_Blue.svg/1200px-Go_Logo_Blue.svg.png)

# golang design pattern
一個專案可能要有設計模式來規劃，這樣在寫程式的時候才可以不會那麼雜亂
來學習一下設計模式
# unit test
```
├── go.mod
├── main.go
└── untils
    ├── untils.go
    └── untils_test.go

```
```go
package untils

import (
	"fmt"
	"testing"
)

type test struct {
	Name  string
	Score int
}

func TestTeststruct(t *testing.T) {
	a := Students{"qwd", 50}
	b := Students{"qwd", 90}

	c :=
		[]test{
			{
				"qwd",
				50,
			},
			{
				"qwd",
				60,
			},
		}

	for _, info := range c {

		if a.check(info.Name) == 0 {
			fmt.Println(a, info.Name, "a check no ok")
			t.Error("wrong result")
		} else if b.check(info.Name) == 0 {
			fmt.Println(b, info.Name, "b check no ok")
			t.Error("wrong result")
		} else {
			fmt.Println(a, info.Name, "both check ok")

			if a.checksco(info.Score) == 2 {
				fmt.Println(a, info.Name, "a no pass")
			} else {
				fmt.Println(a, info.Name, "a pass")
			}
			if b.checksco(info.Score) == 2 {
				fmt.Println(a, info.Name, "b no pass")
			} else {
				fmt.Println(b, info.Name, "b pass")
			}
		}
	}

}

```
```go
package untils

type Students struct {
	Name  string
	Score int
}

func (g *Students) check(checkname string) int {
	if checkname == g.Name {

		return 1
	} else {

		return 0
	}

}

func (g *Students) checksco(avg int) int {
	if g.Score < avg {
		return 2
	} else if g.Score >= avg {
		return 3
	} else if g.Score >= 90 {
		return 4
	}

	return -1
}

```
```go
package main

import (
	"fmt"
	"untilstest/untils"
)

func main() {
	a := untils.Students{"qwd"}
	fmt.Println(a)
}

```
#  decorate pattern
```go
package main

import "fmt"

type Testbox struct {
	price int
}
type ITest interface {
	Add(price int) int
}
type Type1 struct {
	ITest
}

type Type2 struct {
	ITest
}

func (ty1 *Type1) Add(price int) int {
	return price * 10

}
func (ty2 *Type2) Add(price int) int {
	return price * 20

}

func (tb *Testbox) GetTotal() int {
	return tb.price

}
func (tb *Testbox) AddTotal(i ITest, price int) {
	tb.price = tb.price + i.Add(price)
}
func main() {
	a := Testbox{}
	a.AddTotal(&Type1{}, 1)
	a.AddTotal(&Type2{}, 4)
	fmt.Println(a.GetTotal())

}

```

#  command pattern
```go
package main

import "fmt"

type TVConsole struct {
	Pwr Power
}

type Power struct {
	ICommand
	IsOn bool
}

func (p *Power) Exec() {
	p.PressPower()
}

func (p *Power) PressPower() {
	p.IsOn = !p.IsOn
	fmt.Println("POWER NOW IS ", p.IsOn)
}

type Controller struct {
	Buttons []ICommand
}

type ICommand interface {
	Exec()
}

type DefCommand struct {
	ICommand
}

func (df *DefCommand) Exec() {
	fmt.Println("Do nothing!! ")

}

func (c *Controller) ResetButtons() {
	c.Buttons = []ICommand{}
	i := 0
	for i < 10 {
		c.Buttons = append(c.Buttons, &DefCommand{})
		i++
	}

}
func (c *Controller) SetupButton(iBtn int, iCmd ICommand) {
	c.Buttons[iBtn] = iCmd

}
func main() {
	tv := TVConsole{}
	tv.Pwr.PressPower()
	tv.Pwr.PressPower()
	c := Controller{}
	c.ResetButtons()
	fmt.Println(len(c.Buttons))
	c.Buttons[0].Exec()
	c.SetupButton(0, &tv.Pwr)
	c.Buttons[0].Exec()
}

```
# observe
```go
package main

import "fmt"

type Bus struct {
	Obs []IObserve
}

func (b *Bus) Register(o IObserve) {
	b.Obs = append(b.Obs, o)

}
func (b *Bus) Remove(o IObserve) {
	for i := range b.Obs {
		if b.Obs[i] == o {
			b.Obs = append(b.Obs[:i], b.Obs[:i+1]...)
			return
		}

	}

}
func (b *Bus) Notify(s string) {
	for _, o := range b.Obs {
		o.Update(s)
	}

}

type IObserve interface {
	Update(s string)
}
type Station struct {
}

func (st *Station) Update(s string) {
	fmt.Println("Station Update", s)
}

type Passanger struct {
}

func (pa *Passanger) Update(s string) {
	fmt.Println("Passanger Update", s)
}

func main() {
	bus := Bus{}
	// p := &Passanger{}
	s1 := &Station{}
	s2 := &Station{}
	// bus.Register(p)
	bus.Register(s1)
	bus.Register(s2)
	bus.Notify("s01")

	bus.Notify("s02")
}

```

# strategy
```go
package main

import "fmt"

type Sensor struct {
}

func (s *Sensor) TouchIDCard() {
	fmt.Println("touchid")
}

type ComA struct {
	CheckInclock Sensor
}

func (ca *ComA) CheckIn() {
	fmt.Println("Coma CheckIn")
	ca.CheckInclock.TouchIDCard()

}

type PaperCard struct {
}

func (pc *PaperCard) InsertSalayCard() {
	fmt.Println("insert")

}

type ComB struct {
	CheckEq PaperCard
}

func (cb *ComB) CheckIn() {
	fmt.Println("Coma CheckIn")
	cb.CheckEq.InsertSalayCard()

}

func main() {
	a := ComA{
		CheckInclock: Sensor{},
	}

	b := ComB{
		CheckEq: PaperCard{},
	}
	a.CheckIn()
	b.CheckIn()
}

```

# adapter
```go

package main

import (
	"log"
	"strings"
)

type IForex interface {
	CcyPair() string
}
type Forex struct {
	BaseCcy string
	TerCcy  string
}

func (fx *Forex) CcyPair() string {
	return fx.BaseCcy + fx.TerCcy

}

type IStock interface {
	Ticker() string
}

func (s *Stock) Ticker() string {
	return strings.Split(s.TickerName, "-")[0]

}

type Stock struct {
	TickerName string
	IStock
}

type FXAdapter struct {
	IForex
	IStock
}

func (fxa *FXAdapter) Ticker() string {
	return fxa.IForex.CcyPair()
}
func (fxa *FXAdapter) Ticker2() string {
	return fxa.IStock.Ticker()
}

// func (fxa *FXAdapter) Ticker() {
// 	fxa.IForex.CcyPair()
// }
func main() {
	f := Forex{
		BaseCcy: "usd",
		TerCcy:  "twd",
	}

	st := Stock{
		TickerName: "2330-TSMC",
	}

	sta := FXAdapter{
		IForex: &f,
		IStock: &st,
	}
	// log.Println(f.CcyPair())
	// log.Println(st.Ticker())
	log.Println(sta.Ticker())
	log.Println(sta.Ticker2())
}

```
# facotry
```go

package main

import "fmt"

type LaunchBox struct {
	Meal     string
	Tool     string
	stayOrGo string
	Drink    string
}

func (lb *LaunchBox) Order(stayOrGo string, meal string) {
	fmt.Println("接受訂單")
	lb.Meal = meal
	lb.stayOrGo = stayOrGo

}
func (lb *LaunchBox) Prepare() {
	fmt.Println("準備")
	switch lb.stayOrGo {
	case "內用":
		lb.Tool = "餐盤"
		lb.Drink = "湯"
	case "外帶":
		lb.Tool = "塑膠袋"
		lb.Drink = "飲料"
	}

}
func (lb *LaunchBox) Deliver() {
	fmt.Println("訂單", lb.Drink, lb.Meal, lb.Tool)

}
func main() {
	box := LaunchBox{}
	box.Order("外帶", "雞腿飯")
	box.Prepare()
	box.Deliver()
	box.Order("內用", "雞腿飯")
	box.Prepare()
	box.Deliver()

}
```

