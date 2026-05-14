---
title: "Advanced Load Balancing with Traefik Proxy"
source: "https://traefik.io/blog/exploring-advanced-load-balancing-in-kubernetes-with-traefik-proxy"
author:
  - "[[Jakub Hajek]]"
published: 2022-10-06
created: 2026-05-14
description: "In this article, we explore all the methods and benefits of advanced load balancing in Kubernetes that are introduced by Traefik Proxy."
tags:
  - "clippings"
---
![advanced load balancing in kubernetes](https://storage.ghost.io/c/9f/0d/9f0dcb4f-3eeb-4186-b453-8ff9bae963b2/content/images/2022/10/Blog@2x--30--1.jpg)

advanced load balancing in kubernetes

Load balancing is a method of distributing incoming network traffic across a group of backend servers or server pools. [Having a load balancer in your network has significant benefits](https://traefik.io/glossary/load-balancing-101-network-vs-application/), including reduced downtime, scalability, and flexibility.

Nowadays, in the cloud native ecosystem, we can deploy two load balancers and benefit from both. One of them can be running in the **transport layer** (Layer 4) and the second in the **application layer** (Layer 7).

![networking layers based on OSI model](https://storage.ghost.io/c/9f/0d/9f0dcb4f-3eeb-4186-b453-8ff9bae963b2/content/images/2022/10/Diagram.png)

networking layers based on OSI model

- **Layer 4 (L4)** load balancing is mostly related to the network, IP addresses, network address translation or NAT, and packets.
- **Layer 7 (L7)** operates at the highest level of the [OSI model](https://en.wikipedia.org/wiki/OSI_model?ref=traefik.io). The HTTP protocol is the most dominant protocol in that layer. HTTP comes with lots of features that you can use as a factor to decide where to route each incoming request. Basically, in L7 you can create a rule based on URL, you can determine what content type comes with your request, and create rules based on its value.

In this article, I’ll explore advanced load balancing, so I’m focusing on L7, in the context of [Traefik Proxy](https://traefik.io/traefik/). If you need to learn more about the basics of load balancing within Kubernetes, check out our video, [Getting Started with Traefik](https://www.youtube.com/watch?v=CL5Cxxz-yHo&ref=traefik.io).

So, having that principal understanding of load balancing, let’s explore all the methods and benefits of advanced load balancing that are introduced by Traefik Proxy.

## Weighted round robin

Within Traefik Proxy, we have developed an abstraction called Traefik Service, which has a built-in feature that allows you to easily use a weighted round robin (WRR) algorithm.  
  
The major difference between WRR and round robin (RR) is how weights are configured. In the round robin algorithm, you do not influence how traffic is distributed among the backend servers, and they get roughly equal amounts of traffic. Whereas for weighted round robin, you can configure weights for each of the backend servers that are added to the server pool.

The question is, when should the weights be manually configured for weighted RR, and when should I rely on the RR algorithm and its decision process? Well, in some specific use cases, you have some servers that have fewer resources e.g. slower CPU and less memory, compared to other servers that have powerful CPU installed. Based on the weights, you can decide how much traffic will reach a particular server.

That explanation is true for servers; however, in the Kubernetes world, pods, containers, and services communicate with each other. So, let’s have a look at that aspect from the Traefik Proxy perspective.

## Progressive delivery with WRR using the Traefik Service

By progressively changing weights in the WRR algorithm, we can introduce a new way of deploying applications called progressive delivery. Progressive delivery allows you to deploy another version of your app and gradually migrate users from v1 to v2 if the v2 remains stable and there is no regression in the new version.

That process allows the development team to release features quickly and reduce the risk of potential failure caused by an unstable version of the deployed application. That process also allows the QA team to test the application in a live environment which has tremendous benefits. You can try to build pre-production environments similar to production ones, but they will never be the same.

One way WRR can be used for QA is to test a feature based on the feature flag enabled or a specific header added to the request. You can add a specific header that the load balancer will read to redirect users to the newest version. By attaching this header for only some users (in this case, our QA team), we can test the application on production without affecting our users.

Here we should mention the difference between deployment and release. You can deploy an application on a server anytime, but it is not considered released until you have directed network traffic to it.

Some [common deployment strategies](https://traefik.io/glossary/kubernetes-deployment-strategies-blue-green-canary/) include for this include canary release (the most common approach where you shift the network traffic slowly) and blue /green deployment (when you switch the network traffic from one version of the app to another entirely).

## Traffic mirroring

[Traffic mirroring](https://doc.traefik.io/traefik/routing/providers/kubernetes-crd/?ref=traefik.io#mirroring) is a feature that can copy a request to another service without sending back the response to the client. In case of an incorrect response, the user will not be impacted at all.

You can use mirroring to test the new application version without affecting users, limiting the risk to almost zero.

Compared to progressive delivery, in some specific circumstances, even if the majority of users are routed to the previous version, a small percentage ofusers will reach the new version. In case of a failure, the invalid response could be sent back to the user.

Mirroring can be used to test, allowing you to see what is happening on the application by analyzing log files and metrics. This way, you can identify issues without impacting users because responses are not being sent back to the users.

## Sticky sessions

Sticky sessions allow us to always reach one specific backend server in the pool. It is achieved by creating affinity between a client and a backend server based on given criteria e.g. source IP address or a cookie.

Traefik Proxy uses a header Set-Cookie to handle session persistence, so each subsequent client request needs to send the cookie with the given value to keep the session alive. Otherwise, the existing persistence won’t work, and the default algorithm will be used.

In case of failure of the backend server to which the session persistence is created, the client request will be forwarded to another server with the same parameters, and the cookie will be tracked on the new server.

For example, we can imagine an environment consisting of a few Tomcat servers with a load balancer running in front of those Tomcat servers. A user would send an initial request to establish a connection with the application deployed on the Tomcat server — let's call that server Tomcat-1. Without a special mechanism, called session replication, managed on the application server, the load balancer won’t know that a session is already established and will send any subsequent request to another server — e.g., Tomcat-2 forcing Tomcat-2 to establish a new session instead of relying on the session established on Tomcat-1.

In that scenario, a load balancer with a sticky session feature should forward the request to the same Tomcat instance (Tomcat-1) based on the Set-Cookie header. Traefik Proxy is capable of handling that requirement by using the Set-Cookie header.

## Nested health checks

Nested health checks is a Traefik Proxy-specific enhancement and can be used in more advanced use cases, for example:

- Creating a routing rule between two data centers
- Creating a rule between a server that is not exposed through Kubernetes services — e.g., a classical virtual machine running in the same or a separate network — so you can mix the server in the pool by using Kubernetes Service together with an external endpoint that is not exposed inside the same cluster but is exposed by a VM

One of the use cases for nested health checks is migrating a legacy environment to Kubernetes. Imagine that you can build a POC of an existing application on Kubernetes, and at the same time, you can still have the same application running in the traditional way — for example, on multiple VMs. Then by creating the appropriate routing rule, you can use the WRR algorithm to decide where the incoming request should be routed to. You can also add a health check to the backend level to ensure that the target backend is healthy before sending the request to it.

Another example is distributing network traffic across two (or more) data centers. Each data center exposes an endpoint. Each of the endpoints exposes a health check that is constantly verified by Traefik Proxy to ensure that target is healthy and ready to accept incoming connections. In case of failure in one of the data centers, the health check will fail, and Traefik Proxy will not send the request to the unhealthy target/unhealthy endpoint.

The feature is only available in the Traefik File provider. That means that you have to create a file with the entire configuration, add this file as a Kubernetes config map, and then add it to the Traefik Proxy deployment.

## Are you ready to get your hands dirty?

But enough with all the theory — let’s put all this knowledge into practice!

Join me for the free Traefik Academy course on [Advanced Load Balancing with Traefik Proxy](https://academy.traefik.io/courses/advanced-load-balancing-w-traefik-proxy?ref=traefik.io), where we will work through a series of hands-on exercises together to see how everything I discussed in this article will be implemented.

Create your Traefik Academy account for free, and start learning today!

Share article

About the Author