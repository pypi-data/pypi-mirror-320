# COT(PY)DANTIC

Pythonic generation of Coursor-On-Target (COT) messages (xml/protobuf).  
Provides pydantic_xml models with type completion and verification.  
Easy transformation between xml and protobuf.  
Human readable cot type construction.  

## COT/TAK Resources

[takproto](https://takproto.readthedocs.io/en/latest): Encoding of XML to protobuf  
[pydantic_xml](https://pydantic-xml.readthedocs.io/en/latest/): Python pydantic models to XML  
[pytak](https://pytak.readthedocs.io/en/latest/examples/): Wealth of COT/TAK format information  
[cot_types](https://github.com/dB-SPL/cot-types): Cot type to human readable mapping  
[MIL STD 2525](http://everyspec.com/MIL-STD/MIL-STD-2000-2999/MIL-STD-2525B_CHG-2_20725/#:~:text=These%20symbols%20are%20designed%20to%20enhance%20DOD%60s%20joint%20warfighting%20interoperability): cot type symbols  
[tak.gov](https://tak.gov/): Governing body of ATAK, Wintak, and other TAK based protocols  
[dev_guide](https://nps.edu/documents/104517539/109705106/COT+Developer+Guide.pdf/cb125ac8-1ed1-477b-a914-7557c356a303#:~:text=What%20is%20Cursor-on-Target?%20In%20a%20nutshell,): developer outline of COT messages  
[tak_miter](https://www.mitre.org/sites/default/files/pdf/09_4937.pdf): in-depth cot descriptions  

## COTDANTIC CLI Tool

This package includes a curses cli tool.  
Situational Awareness (SA) messages are printed in the main window.  
Contacts are listed in the contacts window.  
Chat messages are listed in the chat window, messages are automatically echoed back to sender.  
Select window with left, right, arrow keys.  
Scroll window with up, down, arrow keys.  
Scroll to end with backspace key.  
Default gateway interface used by default.  
```
cotdantic --help
usage: cotdantic [-h] [--maddress MADDRESS] [--mport MPORT] [--minterface MINTERFACE] [--gaddress GADDRESS] [--gport GPORT] [--ginterface GINTERFACE] [--address ADDRESS] [--interface INTERFACE] [--uport UPORT]
                 [--tport TPORT] [--debug DEBUG] [--unicast {tcp,udp}]

options:
  -h, --help            show this help message and exit
  --maddress MADDRESS   SA address (default: 239.2.3.1)
  --mport MPORT         SA port (default: 6969)
  --minterface MINTERFACE
                        SA interface (default: default-gateway)
  --gaddress GADDRESS   Chat address (default: 224.10.10.1)
  --gport GPORT         Chat port (default: 17012)
  --ginterface GINTERFACE
                        Chat interface (default: default-gateway)
  --address ADDRESS     default TCP/UDP send address (default: default-gateway)
  --interface INTERFACE
                        TCP/UDP bind interface (default: default-gateway)
  --uport UPORT         TCP port (default: 17012)
  --tport TPORT         UDP port (default: 4242)
  --debug DEBUG         Print debug information (default: False)
  --unicast {tcp,udp}   Endpoint protocol (default: tcp)
```

![cli-tool](/images/cli_tool.png)

A docker build is included for multicast docker testing.  
For multicast to reach inside a docker network=host must be set.  

## COT Construction

Object based creation of COT.  
Common fields have default values.  
Optional fields are excluded from XML/Protobuf.  

Creation of COT python model  
```python
from cotdantic import *
from uuid import uuid4

uid = str(uuid4())
cot_type = str(atom.friend.ground.unit.combat.infantry)

point = Point(lat=38.711, lon=-77.147, hae=10, ce=5.0, le=10.0)
contact = Contact(callsign='Delta1', endpoint='192.168.0.100:4242:tcp')
group = Group(name='Cyan', role='Team Member')
detail = Detail(contact=contact, group=group)
cot_model = Event(
	uid=uid,
	type=cot_type,
	point=point,
	detail=detail,
)
```
COT Model  
```python
type='a-f-G-U-C-I' point=Point(lat=38.711, lon=-77.147, hae=10.0, le=10.0, ce=5.0) version=2.0 uid='c56af374-52f6-4c8a-bd1d-8f48e7ebb21b' how='m-g' time='2024-10-12T20:42:31.12Z' start='2024-10-12T20:42:31.12Z' stale='2024-10-12T20:47:31.12Z' qos=None opex=None access=None detail=Detail(contact=Contact(callsign='Delta1', endpoint='192.168.0.100:4242:tcp', phone=None), takv=None, group=Group(name='Cyan', role='Team Member'), status=None, track=None, precision_location=None, link=[], alias=None, image=None, video=None)
```

## COT Conversion
COT XML  
```python
# pretty print requires lxml dependency
xml_b: bytes = cot_model.to_xml(pretty_print=True)
xml_s: str = xml_b.decode()
```
```xml
<event type="a-f-G-U-C-I" version="2.0" uid="c56af374-52f6-4c8a-bd1d-8f48e7ebb21b" how="m-g" time="2024-10-12T20:42:31.12Z" start="2024-10-12T20:42:31.12Z" stale="2024-10-12T20:47:31.12Z">
  <point lat="38.711" lon="-77.147" hae="10.0" le="10.0" ce="5.0"/>
  <detail>
    <contact callsign="Delta1" endpoint="192.168.0.100:4242:tcp"/>
    <__group name="Cyan" role="Team Member"/>
  </detail>
</event>
```
COT PROTOBUF  
```python
proto = bytes(cot_model)
```
```python
b'\xbf\x01\xbf\x12\xb3\x01\n\x0ba-f-G-U-C-I*$c56af374-52f6-4c8a-bd1d-8f48e7ebb21b0\xd0\xde\xdf\x93\xa828\xd0\xde\xdf\x93\xa82@\xb0\x86\xf2\x93\xa82J\x03m-gQ^\xbaI\x0c\x02[C@Y\xc5 \xb0rhIS\xc0a\x00\x00\x00\x00\x00\x00$@i\x00\x00\x00\x00\x00\x00\x14@q\x00\x00\x00\x00\x00\x00$@z7\x12 \n\x16192.168.0.100:4242:tcp\x12\x06Delta1\x1a\x13\n\x04Cyan\x12\x0bTeam Member'
```

## Custom Detail Extension

The below handles custom detail tags.  
```python
from pydantic_xml import attr, element
from typing import Optional
from cotdantic import *


class CustomElement(CotBase, tag='target_description'):
	hair_color: str = attr()
	eye_color: str = attr()


class CustomDetail(Detail):
	description: Optional[CustomElement] = element(default=None)


class CustomEvent(EventBase[CustomDetail]):
	pass

```
Same usage schema for xml and protobuf.  
See tests for more details.  
```python
custom_event = CustomEvent(...)
xml = custom_event.to_xml()
proto = bytes(custom_event)
CustomEvent.from_bytes(proto)
```

Alternativly, if the extention is simplistic, the following can be used to add custom detail elements.  
The below raw_xml will be added to the protobuf and XML.  
```
detail = Detail()
detail.raw_xml = b"<target_description hair_color="red" eye_color="brown"/>"
```

## Raw XML
The protobuf xml detail string is stored in Detail.raw_xml.  
The raw_xml field contains all the XML tags not defined by the model.  
These tags are added back when encoded to protobuf or XML.  


## Cot Types

Development of the available cot types is not comprehensive.  
Eventually all cot types should be accessable from the following type-completing syntax.  
```python
from cotdantic import atom
print(atom.friend.ground.unit.combat.infantry)
```
```
a-f-G-U-C-I
```
