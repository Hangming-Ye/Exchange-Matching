# ECE 568 HW4 XML Format

<create> or <transaction>

## Create <create>

children: <account id="ACCOUNT_ID" balance="BALANCE"/>  <symbol sym="SYM">

**sever: has order requirement**

a.  <account id="ACCOUNT_ID" balance="BALANCE"/>

This creates a new account with the given unique ID and balance (in USD)

b. <symbol sym="SYM">

children: <account id="ACCOUNT_ID"> NUM </account>

**RESPONSE**:

Root node：<results>

children：<created> / <error>

<created> attribute: account id, (sym), 

<error> attribute: account id, (sym),  

**textual body description of the problem** <error> body </error>

## Transactions <transaction>

attribute：ID

Children： <order>/ <cancel>/ <query>

**sever: no order requirement**

a.  <order>

attribute: sym, amount, and limit

> `order`:  An order is a  request to buy or sell. 
>
> `limit`: 	
>
> buy order: This price is the maximum price at which the symbol may be purchased. (positive)
>
> sell orders: the minimum  price at which the symbol may be sold. (negative)

**RESPONSE**:

Root node：<results>

children：<opened> / <error>

<opened> attribute: sym, amount, and limit,  id

<error> attribute: sym, amount,  and limit

**textual body description of the problem** <error> body </error>

b.  <query>

attribute: ID

**RESPONSE**:

Root node: <status>

attribute: id

children:  <open shares =... >  <canceled shares=... time=...>  <executed shares=... price=... time=.../>

time: in seconds since the epoch

c.  <cancel>

attribute: ID

**RESPONSE**:

Root node: <canceled>

children:  <canceled shares=... time=...> / <executed shares=... price=... time=.../>



# Match Strategy

(a)	give the best price match	(seller’s	limit	price	≤	execution	price	≤	buyer’s	limit	price)

(b)	break ties by giving priority to orders that arrived earlier.