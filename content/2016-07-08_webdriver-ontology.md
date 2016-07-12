Title: Untangling WebDriver and the Browser Automation Landscape I Live In
Date: 2016-07-12
Modified: 2016-07-12
Tags: mozilla, foss, web, automation
Slug: webdriver-ontology
Author: Maja Frydrychowicz
Summary: I define WebDriver, W3C WebDriver, Selenium, geckodriver, FirefoxDriver, Marionette harness/runner/client/driver and more.

This piece is about too few names for too many things, as well as a kind of origin story for a web standard. For the past year or so, I've been contributing to a Mozilla project broadly named Marionette -- [a set of tools for automating and testing Gecko-based browsers like Firefox](http://vakila.github.io/blog/marionette-act-i-automation/). Marionette is part of a larger browser automation universe that I've managed to mostly ignore so far, but the time has finally come to make sense of it.

The main challenge for me has been nailing down imprecise terms that have changed over time. From my perspective, "Marionette" may refer to any combination of two to four things, and it's related to equally vague names like "Selenium" and "WebDriver"... and then there are things like "FirefoxDriver" and "geckodriver". Blargh. Untangling needed.

_Aside: integrating a new team member (like, say, a volunteer contributor or an intern) is the best! They ask big questions and you get to teach them things, which leads to filling in your own knowledge. Everyone wins._

## The W3C WebDriver Specification

Okay, so let's work our way backwards, starting from the future. ("The future is now.") We want to remotely control browsers so that we can do things like write [automated tests for the content they run](https://github.com/davehunt/bedrock/blob/e1580816fcedbd3e6fc7d7b95a06270d6cd4f08e/tests/functional/test_navigation.py#L12-L23) or [tests for the browser UI itself](http://www.hskupin.info/2016/06/02/firefox-ui-tests-platform-operations-project-of-the-month/). It sucks to have to write the same test in a different way for each browser or each platform, so let's have a common interface for testing all browsers on all platforms. (Yay, open web standards!) To this end, a group of people from several organizations is working on the [WebDriver Specification](https://w3c.github.io/webdriver/webdriver-spec.html).

The main idea in this specification is the __WebDriver Protocol__, which provides a platform- and browser- agnostic way to send [commands](https://w3c.github.io/webdriver/webdriver-spec.html#list-of-endpoints) to the browser you want to control, commands like "open a new window" or "execute some JavaScript." It's a communication protocol[^1] where the payload is some JSON data that is sent over HTTP. For example, to tell the browser to navigate to a url, a client sends a POST request to the endpoint `/session/{session id of the browser instance you're talking to}/url` with body `{"url": "http://example.com/"}`.

The server side of the protocol, which might be implemented as a browser add-on or might be built into the browser itself, listens for commands and sends responses. The client side, such as a Python library for automating browsers, send commands and processes the responses.

This broad idea is already implemented and in use: an open source project for browser automation, Selenium WebDriver, became widely adopted and is now the basis for an open web standard. Awesome! (_On the other hand, oh no! The overlapping names begin!_) 

## Selenium WebDriver

Where does this WebDriver concept come from? You may have noticed that lots of web apps are tested across different browsers with [Selenium](http://www.seleniumhq.org/) -- that's precisely what it was built for back in 2004-2009[^2]. One of its components today is __Selenium WebDriver__. 

(_Confusingly[^3], the terms "Selenium Webdriver, "Webdriver", "Selenium 2" and "Selenium" are often used interchangeably, as a consequence of the project's [history](http://www.aosabook.org/en/selenium.html)._)

Selenium WebDriver provides APIs so that you can write code in your favourite language to simulate user actions like this:

```
client.get("https://www.mozilla.org/")
link = client.find_element_by_id("participate")
link.click()
```

Underneath that API, commands are transmitted via JSON over HTTP, as described in the previous section. A fair name for the protocol currently implemented in Selenium is __Selenium JSON Wire Protocol__. We'll come back to this distinction later.

As mentioned before, we need a server side that understands incoming commands and makes the browser do the right thing in response. The Selenium project provides this part too. For example, they wrote __FirefoxDriver__ which is a Firefox add-on that takes care of interpreting WebDriver commands. There's also InternetExplorerDriver, AndroidDriver and more. I imagine it takes a lot of effort to keep these browser-specific "drivers" up-to-date.

### Then something cool happened

A while after Selenium 2 was released, browser vendors started implementing the Selenium JSON Wire Protocol themselves! Yay! This makes a lot of sense: they're in the best position to maintain the server side and they can build the necessary behaviour directly into the browser.

It started with [OperaDriver](https://seleniumhq.wordpress.com/2011/02/09/operadriver_released/) in [2009-2011](https://dev.opera.com/blog/operadriver-now-a-part-of-selenium-and-experimental-android-support-2/), and then others followed such as [ChromeDriver](https://sites.google.com/a/chromium.org/chromedriver/) and Mozilla's [geckodriver](https://github.com/mozilla/geckodriver) with [Marionette](https://developer.mozilla.org/en-US/docs/Mozilla/QA/Marionette).[^4] This is where the motivation for a WebDriver standard comes from.

### Let's Review

Selenium Webdriver (a.k.a. Selenium 2, WebDriver) provides a common API, protocol and browser-specific "drivers" to enable browser automation. Browser vendors started implementing the Selenium JSON Wire Protocol themselves, thus gradually replacing some of Selenium's browser-specific drivers. Since WebDriver is already being implemented by [all](http://www.theautomatedtester.co.uk/blog/2016/the-final-major-player-is-set-to-ship-webdriver.html) major browser vendors to some degree, it's being turned into a rigorous web standard, and some day all browsers will implement it in a perfectly compatible way and we'll all live happily ever after.

Is the Selenium JSON Wire Protocol the same as the W3C WebDriver protocol? Technically, no. The W3C spec is describing the future of WebDriver[^5], but it's based on what Selenium WebDriver and browser vendors are already doing. The goal of the spec is to coordinate the browser automation effort and make sure we're all implementing the same interface; each command in the protocol should mean the same thing across all browsers.

## A Fresh Look at the Marionette Family

Now that I understand the context, my view of Marionette's components is much clearer.

* Marionette Server together with [geckodriver](https://github.com/mozilla/geckodriver) make up Mozilla's implementation of the W3C WebDriver protocol.
* Marionette Server is built directly into Firefox (into the Gecko rendering engine) and it speaks a slightly different protocol. To make Marionette truly WebDriver-compatible, we need to translate between Marionette’s custom protocol and the WebDriver protocol, which is exactly what geckodriver does. The Selenium client can talk to geckodriver, which in turn talks to Marionette Server.
* As I mentioned earlier, the plan for Selenium 3 is to have geckodriver replace Selenium's FirefoxDriver. This is an important change: since FirefoxDriver is a Firefox add-on, it has limitations and is [going to stop working altogether](https://wiki.mozilla.org/Add-ons/Extension_Signing) with future releases.
* [Marionette Client](http://marionette-client.readthedocs.io/en/latest/) is Mozilla's official Python library for remote control of Gecko, but it's not covered by the W3C WebDriver spec and it's not compatible with WebDriver in general. Think of it as an alternative to Selenium's Python client with Gecko-specific features. Selenium + geckodriver should eventually replace Marionette Client, including the Gecko-specific features.
* The Marionette project also includes tools for integrating with Mozilla's intricate test infrastructure: [Marionette Test Runner](https://developer.mozilla.org/en-US/docs/Marionette_Test_Runner), a.k.a. the Marionette test harness. This part of the project has nothing to do with WebDriver, really, except that it knows how to run tests that depend on Marionette Client. The runner collects the tests you ask for, takes care of starting a Marionette session with the right browser instance, runs the tests and reports the results.[^6]

As you can see, "Marionette" may refer to many different things. I think this ambiguity will always make me a little nervous... Words are hard, especially as a loose collection of projects evolves and becomes unified. In a few years, the terms will firm up. For now, let's be extra careful and specify which piece we're talking about. 

## Acknowledgements
Thanks to [David Burns](https://twitter.com/AutomatedTester) for patiently answering my half-baked questions last week, and to James Graham and [Andreas Tolfsen](https://twitter.com/tolfsen) for providing detailed and delightful feedback on a draft of this article. Bonus high-five to [Anjana Vakil](http://vakila.github.io/) for contributions to Marionette Test Runner this year and for inspiring me to write this post in the first place. 

[^1]: Terminology lesson: the WebDriver protocol is a [wire protocol](https://en.wikipedia.org/wiki/Wire_protocol) because it's at the application level and requires several applications working together.
[^2]: I give a range of years because Selenium WebDriver is a merger of two projects that started at different times.
[^3]: Abbreviated Selenium history and roadmap: Selenium 1 used an old API and mechanism called SeleniumRC, Selenium 2 favours the WebDriver API and JSON Wire Protocol, Selenium 3 will officially designate SeleniumRC as deprecated ("LegRC", harhar), and Selenium 4 will implement the authoritative W3C WebDriver spec.
[^4]: Many of my claims about Marionette are confirmed by this [historical artifact from 2012](http://www.theautomatedtester.co.uk/blog/2012/marionette-the-future-of-firefoxdriver-in-selenium.html), which I came across shortly before publishing this post.
[^5]: For example, until recently Selenium WebDriver only included commands that are common to all browsers, with no way to use features that are specific to one. In contrast, the W3C WebDriver spec allows the possibility of [extension commands](https://w3c.github.io/webdriver/webdriver-spec.html#dfn-extension-commands). Extension commands are being implemented in Selenium clients right now! The future is now!
[^6]: Fun fact: Marionette is not only used for "Marionette Tests" at Mozilla. The client/server are also used to instrument Firefox for other test automation like mochitests and Web Platform Tests. 
