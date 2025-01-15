from typing import TypeVar, Generic, Optional, Union, Any, List, get_args
from pydantic_xml import element, attr, xml_field_serializer
from pydantic_xml.element import XmlElementWriter
from pydantic_xml.model import XmlEntityInfo
from functools import partial, lru_cache
import xml.etree.ElementTree as ET
from pydantic import Field
from uuid import uuid4
import pydantic_xml
import datetime


class CotBase(pydantic_xml.BaseXmlModel, search_mode='unordered'):
	def to_xml(
		self,
		*,
		skip_empty: bool = False,
		exclude_none: bool = True,
		exclude_unset: bool = False,
		**kwargs: Any,
	) -> Union[str, bytes]:
		return super().to_xml(
			skip_empty=skip_empty,
			exclude_none=exclude_none,
			exclude_unset=exclude_unset,
			**kwargs,
		)


T = TypeVar('T', bound=CotBase)


def datetime2iso(time: datetime.datetime):
	# return f'{time.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-4]}Z'
	return f'{time.strftime("%Y-%m-%dT%H:%M:%S.%f")}Z'


def epoch2iso(epoch: int):
	time = datetime.datetime.fromtimestamp(epoch / 1000, tz=datetime.timezone.utc)
	return datetime2iso(time)


def iso2epoch(iso: str) -> int:
	if '.' in iso:
		time = datetime.datetime.strptime(iso, '%Y-%m-%dT%H:%M:%S.%fZ').replace(tzinfo=datetime.timezone.utc)
	else:
		time = datetime.datetime.strptime(iso, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=datetime.timezone.utc)
	return int(time.timestamp() * 1000)


def isotime(hours: int = 0, minutes: int = 0, seconds: int = 0) -> str:
	current = datetime.datetime.now(datetime.timezone.utc)
	offset = datetime.timedelta(hours=hours, minutes=minutes, seconds=seconds)
	time = current + offset
	return datetime2iso(time)


class Point(CotBase, tag='point'):
	lat: float = attr()
	lon: float = attr()
	hae: float = attr(default=999999)
	le: float = attr(default=999999)
	ce: float = attr(default=999999)


class Contact(CotBase, tag='contact'):
	endpoint: Optional[str] = attr(default=None)
	phone: Optional[str] = attr(default=None)
	callsign: Optional[str] = attr(default=None)


class Usericon(CotBase, tag='usericon'):
	iconsetpath: Optional[str] = attr(default=None)


class Height(CotBase, tag='height'):
	value: Optional[float] = attr(default=None)
	height: Optional[float] = None


class Clamped(CotBase, tag='clamped'):
	value: Optional[bool] = attr(default=None)


class StrokeColor(CotBase, tag='strokeColor'):
	value: Optional[int] = attr(default=None)


class StrokeStyle(CotBase, tag='strokeStyle'):
	value: Optional[str] = attr(default=None)


class StrokeWeight(CotBase, tag='strokeWeight'):
	value: Optional[int] = attr(default=None)


class FillColor(CotBase, tag='fillColor'):
	value: Optional[int] = attr(default=None)


class HeightUnit(CotBase, tag='height_unit'):
	value: Optional[int] = attr(default=None)
	unit: Optional[int] = None


class Alpha(CotBase, tag='alpha'):
	value: Optional[int] = None


class Width(CotBase, tag='width'):
	width: Optional[int] = None


class Color(CotBase, tag='color'):
	color: Optional[str] = None


class LineStyle(CotBase, tag='LineStyle'):
	color: Optional[Color] = element(default=None)
	width: Optional[Width] = element(default=None)
	alpha: Optional[Alpha] = element(default=None)


class PolyStyle(CotBase, tag='PolyStyle'):
	color: Optional[Color] = element(default=None)


class Style(CotBase, tag='Style'):
	line_style: Optional[LineStyle] = element(default=None)
	poly_style: Optional[PolyStyle] = element(default=None)


class Ellipse(CotBase, tag='ellipse'):
	minor: Optional[float] = attr(default=None)
	angle: Optional[float] = attr(default=None)
	major: Optional[float] = attr(deafult=None)


class Link(CotBase, tag='link'):
	style: Optional[Style] = element(default=None)
	type: Optional[str] = attr(default=None)
	uid: Optional[str] = attr(default=None)
	parent_callsign: Optional[str] = attr(default=None)
	relation: Optional[str] = attr(default=None)
	remarks: Optional[str] = attr(default=None)
	production_time: Optional[str] = attr(default=None)
	point: Optional[str] = attr(default=None)
	callsign: Optional[str] = attr(default=None)


class Shape(CotBase, tag='shape'):
	ellipse: Optional[Ellipse] = element(default=None)
	link: List[Link] = element(default=[])


class Status(CotBase, tag='status'):
	readiness: Optional[bool] = attr(default=None)
	battery: Optional[int] = attr(default=None)


class Group(CotBase, tag='__group'):
	name: Optional[str] = attr()
	role: Optional[str] = attr()


class Takv(CotBase, tag='takv'):
	device: Optional[str] = attr()
	platform: Optional[str] = attr()
	os: Optional[str] = attr()
	version: Optional[str] = attr()


class Track(CotBase, tag='track'):
	speed: Optional[float] = attr()
	course: Optional[float] = attr()


class PrecisionLocation(CotBase, tag='precisionlocation'):
	geopointsrc: Optional[str] = attr(default=None)
	altsrc: Optional[str] = attr(default=None)


class Alias(CotBase, tag='uid'):
	Droid: Optional[str] = attr(default=None)


class Image(CotBase, tag='image'):
	bytes: str
	size: int = attr()
	height: int = attr()
	width: int = attr()
	mine: str = attr(default='image/jpg')
	type: str = attr(default='EO')


class Attachment(CotBase, tag='attachment'):
	type: Optional[str] = attr(default=None)
	xml: Optional[str] = attr(default=None)


class SendData(CotBase, tag='sendData'):
	sent: Optional[int] = attr(default=None)


class Archive(CotBase, tag='archive'):
	pass


class ConnectionEntry(CotBase, tag='ConnectionEntry'):
	protocol: str = attr()
	path: str = attr()
	address: str = attr()
	port: int = attr()
	uid: str = attr()
	alias: str = attr()
	rover_port: int = attr(name='roverPort')
	rtsp_reliable: int = attr(name='rtspReliable')
	ignore_embedded_klv: bool = attr(name='ignoreEmbeddedKLV')
	network_timout: int = attr(name='networkTimeout')
	buffer_time: int = attr(name='bufferTime')


class Video(CotBase, tag='__video'):
	connection_entry: ConnectionEntry = element()


class Remarks(CotBase, tag='remarks'):
	text: Optional[str] = None
	source: Optional[str] = attr(default=None)
	source_id: Optional[str] = attr(name='sourceID', default=None)
	to: Optional[str] = attr(default=None)
	time: Optional[str] = attr(default_factory=isotime)


class ServerDestination(CotBase, tag='__serverdestination'):
	destinations: Optional[str] = attr(default=None)


class ChatGroup(CotBase, tag='chatgrp'):
	id: Optional[str] = attr(default=None)
	uid0: Optional[str] = attr(default=None)
	uid1: Optional[str] = attr(default=None)


class RangeUnits(CotBase, tag='rangeUnits'):
	value: Optional[int] = attr(default=None)


class Chat(CotBase, tag='__chat'):
	id: Optional[str] = attr(default=None)
	chatroom: Optional[str] = attr(default=None)
	sender_callsign: Optional[str] = attr(name='senderCallsign', default=None)
	group_owner: Optional[bool] = attr(name='groupOwner', default=None)
	message_id: Optional[str] = attr(name='messageId', default=None)
	parent: Optional[str] = attr(default=None)
	chatgrp: Optional[ChatGroup] = element(default=None)


class Hud(CotBase, tag='hud'):
	role: Optional[str] = attr(default=None)


class Planning(CotBase, tag='planning'):
	session_id: Optional[str] = attr(name='sessionId', default=None)


class TakDataPackage(CotBase, tag='takDataPackage'):
	name: Optional[str] = attr(default=None)


class VMF(CotBase, tag='vmf'):
	pass


class Color(CotBase, tag='color'):
	value: Optional[int] = attr(default=None)
	argb: Optional[int] = attr(default=None)


class UniqueID(CotBase, tag='uid'):
	droid: Optional[str] = attr(default=None, name='Droid')


class Range(CotBase, tag='range'):
	value: Optional[float] = attr(default=None)


class NorthRef(CotBase, tag='northRef'):
	value: Optional[float] = attr(default=None)


class BearingUnits(CotBase, tag='bearingUnits'):
	value: Optional[float] = attr(default=None)


class Bearing(CotBase, tag='bearing'):
	value: Optional[float] = attr(default=None)


class Inclination(CotBase, tag='inclination'):
	value: Optional[float] = attr(default=None)


class Navcues(CotBase, tag='__navcues'):
	pass


class BullsEye(CotBase, tag='bullseye'):
	title: Optional[str] = attr(default=None)
	edge_to_center: Optional[bool] = attr(name='edgeToCenter', default=None)
	mils: Optional[bool] = attr(default=None)
	has_range_rings: Optional[bool] = attr(name='hasRangeRings', default=None)
	ring_dist: Optional[float] = attr(name='ringDist', default=None)
	range_ring_visible: Optional[bool] = attr(name='rangeRingVisible', default=None)
	distance: Optional[float] = attr(default=None)
	bullseye_uid: Optional[str] = attr(name='bullseyeUID', default=None)
	bearing_ref: Optional[str] = attr(name='bearingRef', default=None)


class RouteInfo(CotBase, tag='__routeinfo'):
	navcues: Optional[Navcues] = element(default=None)


class AckRequest(CotBase, tag='ack_request'):
	uid: Optional[str] = attr(default=None)
	tag: Optional[str] = attr(default=None)
	ack_requested: Optional[bool] = attr(default=None)


class FileShare(CotBase, tag='fileshare'):
	filename: Optional[str] = attr(default=None)
	sender_url: Optional[str] = attr(name='senderUrl', default=None)
	size_in_bytes: Optional[int] = attr(name='sizeInBytes', default=None)
	sha256: Optional[str] = attr(default=None)
	sender_uid: Optional[str] = attr(name='senderUid', default=None)
	sender_callsign: Optional[str] = attr(name='senderCallsign', default=None)
	name: Optional[str] = attr(default=None)
	peer_hosted: Optional[bool] = attr(name='peerHosted', default=None)


class Detail(CotBase, tag='detail'):
	raw_xml: bytes = Field(exclude=False, default=b'')
	contact: Optional[Contact] = element(default=None)
	chat: Optional[Chat] = element(default=None)
	link: List[Link] = element(default=[])
	takv: Optional[Takv] = element(default=None)
	group: Optional[Group] = element(default=None)
	status: Optional[Status] = element(default=None)
	track: Optional[Track] = element(default=None)
	precision_location: Optional[PrecisionLocation] = element(default=None)
	alias: Optional[Alias] = element(default=None)
	vmf: Optional[VMF] = element(default=None)
	image: Optional[Image] = element(default=None)
	video: Optional[Video] = element(default=None)
	archive: Optional[Archive] = element(default=None)
	usericon: Optional[Usericon] = element(default=None)
	height_unit: Optional[HeightUnit] = element(default=None)
	server_destination: Optional[ServerDestination] = element(default=None)
	attachemnt: Optional[Attachment] = element(default=None)
	send_data: Optional[SendData] = element(default=None)
	tak_data_package: Optional[TakDataPackage] = element(default=None)
	hud: Optional[Hud] = element(default=None)
	planning: Optional[Planning] = element(default=None)
	remarks: Optional[Remarks] = element(default=None)
	color: Optional[Color] = element(default=None)
	uid: Optional[UniqueID] = element(default=None)
	height: Optional[Height] = element(default=None)
	clamped: Optional[Clamped] = element(default=None)
	stroke_color: Optional[StrokeColor] = element(default=None)
	stroke_style: Optional[StrokeStyle] = element(default=None)
	stroke_weight: Optional[StrokeWeight] = element(default=None)
	fill_color: Optional[FillColor] = element(default=None)
	shape: Optional[Shape] = element(default=None)
	file_share: Optional[FileShare] = element(default=None)
	ack_request: Optional[AckRequest] = element(default=None)
	range_units: Optional[RangeUnits] = element(default=None)
	bulls_eye: Optional[BullsEye] = element(default=None)
	inclination: Optional[Inclination] = element(default=None)
	north_ref: Optional[NorthRef] = element(default=None)
	bearingUnits: Optional[BearingUnits] = element(default=None)
	bearing: Optional[Bearing] = element(default=None)
	range: Optional[Range] = element(default=None)

	@classmethod
	@lru_cache
	def tags(cls) -> List[str]:
		detail_tags = []
		for _, info in cls.model_fields.items():
			if not isinstance(info, XmlEntityInfo):
				continue
			types_in_union = get_args(info.annotation)
			custom_type = types_in_union[0]
			detail_tags.append(custom_type.__xml_tag__)
		return detail_tags

	@xml_field_serializer('raw_xml')
	def serialize_detail_with_string(self, element: XmlElementWriter, value: bytes, field_name: str) -> None:
		if len(value) == 0:
			return

		def _recursive_serialize(parent_element: XmlElementWriter, xml_string: str):
			for child in ET.fromstring(xml_string):
				child_element = parent_element.make_element(tag=child.tag, nsmap=None)

				child_element.set_text(child.text)
				for key, val in child.attrib.items():
					child_element.set_attribute(key, val)

				parent_element.append_element(child_element)

				if len(child) > 0:
					_recursive_serialize(child_element, ET.tostring(child).decode())

		_recursive_serialize(element, f'<_raw>{value.decode()}</_raw>')


class TakControl(CotBase):
	minProtoVersion: int = 0
	maxProtoVersion: int = 0
	contactUid: str = ''


class EventBase(CotBase, Generic[T], tag='event'):
	tak_control: TakControl = Field(exclude=True, default_factory=lambda: TakControl())
	type: str = attr()
	point: Point = element()
	version: float = attr(default=2.0)
	uid: str = attr(default_factory=lambda: str(uuid4()))
	how: Optional[str] = attr(default='m-g')
	time: str = attr(default_factory=isotime)
	start: str = attr(default_factory=isotime)
	stale: str = attr(default_factory=partial(isotime, minutes=5))
	qos: Optional[str] = attr(default=None)
	opex: Optional[str] = attr(default=None)
	access: Optional[str] = attr(default=None)
	detail: Optional[T] = element(default=None)

	def __bytes__(self) -> bytes:
		raise NotImplementedError('attached in __init__.py')

	def to_bytes(self) -> bytes:
		raise NotImplementedError('attached in __init__.py')

	@classmethod
	def from_bytes(cls, proto: bytes) -> 'EventBase[T]':
		raise NotImplementedError('attached in __init__.py')


class Event(EventBase[Detail]):
	""""""
