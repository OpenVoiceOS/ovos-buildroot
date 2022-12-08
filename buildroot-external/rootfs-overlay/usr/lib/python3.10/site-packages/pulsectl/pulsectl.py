# -*- coding: utf-8 -*-
from __future__ import print_function

import itertools as it, operator as op, functools as ft
from collections import defaultdict
from contextlib import contextmanager
import os, sys, inspect, traceback

from . import _pulsectl as c


if sys.version_info.major >= 3:
	long, unicode, print_err = int, str, ft.partial(print, file=sys.stderr, flush=True)
else:
	range, map = xrange, it.imap
	def print_err(*args, **kws):
		kws.setdefault('file', sys.stderr)
		print(*args, **kws)
		kws['file'].flush()

is_str = lambda v,ext=None,native=False: (
	isinstance(v, ( (unicode, bytes)
		if not native else (str,) ) + ((ext,) if ext else ())) )
is_str_native = ft.partial(is_str, native=True)
is_num = lambda v: isinstance(v, (int, float, long))
is_list = lambda v: isinstance(v, (tuple, list))
is_dict = lambda v: isinstance(v, dict)

def assert_pulse_object(obj):
	if not isinstance(obj, PulseObject):
		raise TypeError( 'Pulse<something>Info'
			' object is required instead of value: [{}] {}', type(obj), obj )


@ft.total_ordering
class EnumValue(object):
	'String-based enum value, comparable to native strings.'
	__slots__ = '_t', '_value', '_c_val'
	def __init__(self, t, value, c_value=None):
		self._t, self._value, self._c_val = t, value, c_value
	def __repr__(self): return '<EnumValue {}={}>'.format(self._t, self._value)
	def __eq__(self, val):
		if isinstance(val, EnumValue): val = val._value
		return self._value == val
	def __ne__(self, val): return not (self == val)
	def __lt__(self, val):
		if isinstance(val, EnumValue): val = val._value
		return self._value < val
	def __hash__(self): return hash(self._value)

class Enum(object):

	def __init__(self, name, values_or_map):
		vals = values_or_map
		if is_str_native(vals): vals = vals.split()
		if is_list(vals): vals = zip(it.repeat(None), vals)
		if is_dict(vals): vals = vals.items()
		self._name, self._values, self._c_vals = name, dict(), dict()
		for c_val, k in vals:
			v = EnumValue(name, k, c_val)
			setattr(self, k, v)
			self._c_vals[c_val] = self._values[k] = v

	def __getitem__(self, k, *default):
		if isinstance(k, EnumValue):
			t, k, v = k._t, k._value, k
			if t != self._name: raise KeyError(v)
		try: return getattr(self, k, *default)
		except AttributeError: raise KeyError(k)

	def _get(self, k, default=None): return self.__getitem__(k, default)
	def __contains__(self, k): return self._get(k) is not None

	def _c_val(self, c_val, default=KeyError):
		v = self._c_vals.get(c_val)
		if v is not None: return v
		if default is not KeyError:
			return EnumValue(self._name, default, c_val)
		raise KeyError(c_val)

	def __repr__(self):
		return '<Enum {} [{}]>'.format(self._name, ' '.join(sorted(self._values.keys())))


PulseEventTypeEnum = Enum('event-type', c.PA_EVENT_TYPE_MAP)
PulseEventFacilityEnum = Enum('event-facility', c.PA_EVENT_FACILITY_MAP)
PulseEventMaskEnum = Enum('event-mask', c.PA_EVENT_MASK_MAP)

PulseStateEnum = Enum('sink/source-state', c.PA_OBJ_STATE_MAP)
PulseUpdateEnum = Enum('update-type', c.PA_UPDATE_MAP)
PulsePortAvailableEnum = Enum('available', c.PA_PORT_AVAILABLE_MAP)
PulseDirectionEnum = Enum('direction', c.PA_DIRECTION_MAP)


class PulseError(Exception): pass
class PulseOperationFailed(PulseError): pass
class PulseOperationInvalid(PulseOperationFailed): pass
class PulseIndexError(PulseError): pass

class PulseLoopStop(Exception): pass
class PulseDisconnected(Exception): pass

class PulseObject(object):

	c_struct_wrappers = dict()

	def __init__(self, struct=None, *field_data_list, **field_data_dict):
		field_data, fields = dict(), getattr(self, 'c_struct_fields', list())
		if is_str_native(fields): fields = self.c_struct_fields = fields.split()
		if field_data_list: field_data.update(zip(fields, field_data_list))
		if field_data_dict: field_data.update(field_data_dict)
		if struct is None: field_data, struct = dict(), field_data
		assert not set(field_data.keys()).difference(fields)
		if field_data: self._copy_struct_fields(field_data, fields=field_data.keys())
		self._copy_struct_fields(struct, fields=set(fields).difference(field_data.keys()))

		if struct:
			if hasattr(struct, 'proplist'):
				self.proplist, state = dict(), c.c_void_p()
				while True:
					k = c.pa.proplist_iterate(struct.proplist, c.byref(state))
					if not k: break
					self.proplist[c.force_str(k)] = c.force_str(c.pa.proplist_gets(struct.proplist, k))
			if hasattr(struct, 'volume'):
				self.volume = self._get_wrapper(PulseVolumeInfo)(struct.volume)
			if hasattr(struct, 'n_ports'):
				cls_port = self._get_wrapper(PulsePortInfo)
				self.port_list = list(
					cls_port(struct.ports[n].contents) for n in range(struct.n_ports) )
			if hasattr(struct, 'active_port'):
				cls_port = self._get_wrapper(PulsePortInfo)
				self.port_active = (
					None if not struct.active_port else cls_port(struct.active_port.contents) )
			if hasattr(struct, 'channel_map'):
				self.channel_count, self.channel_list = struct.channel_map.channels, list()
				if self.channel_count > 0:
					s = c.create_string_buffer(b'\0' * 512)
					c.pa.channel_map_snprint(s, len(s), struct.channel_map)
					self.channel_list.extend(map(c.force_str, s.value.strip().split(b',')))
			if hasattr(struct, 'state'):
				self.state = PulseStateEnum._c_val(
					struct.state, u'state.{}'.format(struct.state) )
				self.state_values = sorted(PulseStateEnum._values.values())
			self._init_from_struct(struct)

	def _get_wrapper(self, cls_base):
		return self.c_struct_wrappers.get(cls_base, cls_base)

	def _copy_struct_fields(self, struct, fields=None, str_errors='strict'):
		if not fields: fields = self.c_struct_fields
		for k in fields:
			setattr(self, k, c.force_str( getattr(struct, k)
				if not is_dict(struct) else struct[k], str_errors ))

	def _init_from_struct(self, struct): pass # to parse fields in subclasses

	def _as_str(self, ext=None, fields=None, **kws):
		kws = list(it.starmap('{}={}'.format, kws.items()))
		if fields:
			if is_str_native(fields): fields = fields.split()
			kws.extend('{}={!r}'.format(k, getattr(self, k)) for k in fields)
		kws = sorted(kws)
		if ext: kws.append(str(ext))
		return ', '.join(kws)

	def __str__(self):
		return self._as_str(fields=self.c_struct_fields)

	def __repr__(self):
		return '<{} at {:x} - {}>'.format(self.__class__.__name__, id(self), str(self))


class PulsePortInfo(PulseObject):
	c_struct_fields = 'name description available priority'

	def _init_from_struct(self, struct):
		self.available = PulsePortAvailableEnum._c_val(struct.available)
		self.available_state = self.available # for compatibility with <=17.6.0

	def __eq__(self, o):
		if not isinstance(o, PulsePortInfo): raise TypeError(o)
		return self.name == o.name

	def __hash__(self): return hash(self.name)

class PulseClientInfo(PulseObject):
	c_struct_fields = 'name index driver owner_module'

class PulseServerInfo(PulseObject):
	c_struct_fields = ( 'user_name host_name'
		' server_version server_name default_sink_name default_source_name cookie' )

class PulseModuleInfo(PulseObject):
	c_struct_fields = 'index name argument n_used auto_unload'

class PulseSinkInfo(PulseObject):
	c_struct_fields = ( 'index name mute'
		' description sample_spec owner_module latency driver'
		' monitor_source monitor_source_name flags configured_latency card' )

	def __str__(self):
		return self._as_str(self.volume, fields='index name description mute')

class PulseSinkInputInfo(PulseObject):
	c_struct_fields = ( 'index name mute client'
		' owner_module sink sample_spec'
		' buffer_usec sink_usec resample_method driver' )

	def __str__(self):
		return self._as_str(fields='index name mute')

class PulseSourceInfo(PulseObject):
	c_struct_fields = ( 'index name mute'
		' description sample_spec owner_module latency driver monitor_of_sink'
		' monitor_of_sink_name flags configured_latency card' )

	def __str__(self):
		return self._as_str(self.volume, fields='index name description mute')

class PulseSourceOutputInfo(PulseObject):
	c_struct_fields = ( 'index name mute client'
		' owner_module source sample_spec'
		' buffer_usec source_usec resample_method driver' )

	def __str__(self):
		return self._as_str(fields='index name mute')

class PulseCardProfileInfo(PulseObject):
	c_struct_fields = 'name description n_sinks n_sources priority'

class PulseCardPortInfo(PulsePortInfo):
	c_struct_fields = 'name description priority direction latency_offset'

	def _init_from_struct(self, struct):
		self.direction = PulseDirectionEnum._c_val(struct.direction)

class PulseCardInfo(PulseObject):
	c_struct_fields = 'name index driver owner_module n_profiles'
	c_struct_wrappers = {PulsePortInfo: PulseCardPortInfo}

	def __init__(self, struct):
		super(PulseCardInfo, self).__init__(struct)
		self.profile_list = list(
			PulseCardProfileInfo(struct.profiles[n]) for n in range(self.n_profiles) )
		self.profile_active = PulseCardProfileInfo(struct.active_profile.contents)

	def __str__(self):
		return self._as_str(
			fields='name index driver n_profiles',
			profile_active='[{}]'.format(self.profile_active.name) )

class PulseVolumeInfo(PulseObject):

	def __init__(self, struct_or_values=None, channels=None):
		if is_num(struct_or_values):
			assert channels is not None, 'Channel count specified if volume value is not a list.'
			self.values = [struct_or_values] * channels
		elif is_list(struct_or_values): self.values = struct_or_values
		else:
			self.values = list( (x / c.PA_VOLUME_NORM)
				for x in map(float, struct_or_values.values[:struct_or_values.channels]) )

	@property
	def value_flat(self): return (sum(self.values) / float(len(self.values))) if self.values else 0
	@value_flat.setter
	def value_flat(self, v): self.values = [v] * len(self.values)

	def to_struct(self):
		return c.PA_CVOLUME(
			len(self.values), tuple(min( c.PA_VOLUME_UI_MAX,
					int(round(v * c.PA_VOLUME_NORM)) ) for v in self.values) )

	def __str__(self):
		return self._as_str(
			channels=len(self.values), volumes='[{}]'.format(
				' '.join('{}%'.format(int(round(v*100))) for v in self.values) ) )

class PulseExtStreamRestoreInfo(PulseObject):
	c_struct_fields = 'name channel_map volume mute device'

	@classmethod
	def struct_from_value( cls, name, volume,
			channel_list=None, mute=False, device=None ):
		'Same arguments as with class instance init.'
		chan_map = c.PA_CHANNEL_MAP()
		if not channel_list: c.pa.channel_map_init_mono(chan_map)
		else:
			if not is_str(channel_list):
				channel_list = b','.join(map(c.force_bytes, channel_list))
			c.pa.channel_map_parse(chan_map, channel_list)
		if not isinstance(volume, PulseVolumeInfo):
			volume = PulseVolumeInfo(volume, chan_map.channels)
		struct = c.PA_EXT_STREAM_RESTORE_INFO(
			name=c.force_bytes(name),
			mute=int(bool(mute)), device=c.force_bytes(device),
			channel_map=chan_map, volume=volume.to_struct() )
		return struct

	def __init__( self, struct_or_name=None,
			volume=None, channel_list=None, mute=False, device=None ):
		'''If string name is passed instead of C struct, will be initialized from args/kws.
			"volume" can be either a float number
				(same level for all channels) or list (value per channel).
			"channel_list" can be a pulse channel map string (comma-separated) or list
				of channel names. Defaults to stereo map, should probably match volume channels.
			"device" - name of sink/source or None (default).'''
		if is_str(struct_or_name):
			struct_or_name = self.struct_from_value(
				struct_or_name, volume, channel_list, mute, device )
		super(PulseExtStreamRestoreInfo, self).__init__(struct_or_name)

	def to_struct(self):
		return self.struct_from_value(**dict(
			(k, getattr(self, k)) for k in 'name volume channel_list mute device'.split() ))

	def __str__(self):
		return self._as_str(self.volume, fields='name mute device')

class PulseEventInfo(PulseObject):

	def __init__(self, ev_t, facility, index):
		self.t, self.facility, self.index = ev_t, facility, index

	def __str__(self):
		return self._as_str(fields='t facility index'.split())


class Pulse(object):

	def __init__(self, client_name=None, server=None, connect=True, threading_lock=False):
		'''Connects to specified pulse server by default.
			Specifying "connect=False" here prevents that, but be sure to call connect() later.
			"connect=False" can also be used here to
				have control over options passed to connect() method.
			"threading_lock" option (either bool or lock instance) can be used to wrap
				non-threadsafe eventloop polling (can only be done from one thread at a time)
				into a mutex lock, and should only be needed if same-instance methods
				will/should/might be called from different threads at the same time.'''
		self.name = client_name or 'pulsectl'
		self.server, self.connected = server, None
		self._ret = self._ctx = self._loop = self._api = None
		self._actions, self._action_ids = dict(),\
			it.chain.from_iterable(map(range, it.repeat(2**30)))
		self.init()
		if threading_lock:
			if threading_lock is True:
				import threading
				threading_lock = threading.Lock()
			self._loop_lock = threading_lock
		if connect:
			try: self.connect(autospawn=True)
			except PulseError:
				self.close()
				raise

	def init(self):
		self._pa_state_cb = c.PA_STATE_CB_T(self._pulse_state_cb)
		self._pa_subscribe_cb = c.PA_SUBSCRIBE_CB_T(self._pulse_subscribe_cb)

		self._loop, self._loop_lock = c.pa.mainloop_new(), None
		self._loop_running = self._loop_closed = False
		self._api = c.pa.mainloop_get_api(self._loop)

		self._ctx, self._ret = c.pa.context_new(self._api, self.name), c.pa.return_value()
		c.pa.context_set_state_callback(self._ctx, self._pa_state_cb, None)

		c.pa.context_set_subscribe_callback(self._ctx, self._pa_subscribe_cb, None)
		self.event_types = sorted(PulseEventTypeEnum._values.values())
		self.event_facilities = sorted(PulseEventFacilityEnum._values.values())
		self.event_masks = sorted(PulseEventMaskEnum._values.values())
		self.event_callback = None

	def connect(self, autospawn=False, wait=False):
		'''Connect to pulseaudio server.
			"autospawn" option will start new pulse daemon, if necessary.
			Specifying "wait" option will make function block until pulseaudio server appears.'''
		if self._loop_closed:
			raise PulseError('Eventloop object was already'
				' destroyed and cannot be reused from this instance.')
		flags, self.connected = 0, None
		if not autospawn: flags |= c.PA_CONTEXT_NOAUTOSPAWN
		if wait: flags |= c.PA_CONTEXT_NOFAIL
		try: c.pa.context_connect(self._ctx, self.server, flags, None)
		except c.pa.CallError: self.connected = False
		while self.connected is None: self._pulse_iterate()
		if self.connected is False: raise PulseError('Failed to connect to pulseaudio server')

	def disconnect(self):
		if not self._ctx or not self.connected: return
		c.pa.context_disconnect(self._ctx)

	def close(self):
		if self._loop:
			if self._loop_running:
				self._loop_closed = True
				c.pa.mainloop_quit(self._loop, 0)
				return
			try:
				self.disconnect()
				c.pa.mainloop_free(self._loop)
			finally: self._ctx = self._loop = None

	def __enter__(self): return self
	def __exit__(self, err_t, err, err_tb): self.close()


	def _pulse_state_cb(self, ctx, userdata):
		state = c.pa.context_get_state(ctx)
		if state >= c.PA_CONTEXT_READY:
			if state == c.PA_CONTEXT_READY: self.connected = True
			elif state in [c.PA_CONTEXT_FAILED, c.PA_CONTEXT_TERMINATED]:
				self.connected, self._loop_stop = False, True
		return 0

	def _pulse_subscribe_cb(self, ctx, ev, idx, userdata):
		if not self.event_callback: return
		n = ev & c.PA_SUBSCRIPTION_EVENT_FACILITY_MASK
		ev_fac = PulseEventFacilityEnum._c_val(n, 'ev.facility.{}'.format(n))
		n = ev & c.PA_SUBSCRIPTION_EVENT_TYPE_MASK
		ev_t = PulseEventTypeEnum._c_val(n, 'ev.type.{}'.format(n))
		try: self.event_callback(PulseEventInfo(ev_t, ev_fac, idx))
		except PulseLoopStop: self._loop_stop = True

	def _pulse_poll_cb(self, func, func_err, ufds, nfds, timeout, userdata):
		fd_list = list(ufds[n] for n in range(nfds))
		try: nfds = func(fd_list, timeout / 1000.0)
		except Exception as err:
			func_err(*sys.exc_info())
			return -1
		return nfds

	@contextmanager
	def _pulse_loop(self):
		if self._loop_lock: self._loop_lock.acquire()
		try:
			if self._loop_running:
				raise PulseError(
					'Running blocking pulse operations from pulse eventloop callbacks'
						' or other threads while loop is running is not supported by this python module.'
					' Supporting this would require threads or proper asyncio/twisted-like async code.'
					' Workaround can be to stop the loop'
						' (raise PulseLoopStop in callback or event_loop_stop() from another thread),'
						' doing whatever pulse calls synchronously and then resuming event_listen() loop.' )
			self._loop_running, self._loop_stop = True, False
			try: yield self._loop
			finally:
				self._loop_running = False
				if self._loop_closed: self.close() # to free() after stopping it
		finally:
			if self._loop_lock: self._loop_lock.release()

	def _pulse_run(self):
		with self._pulse_loop() as loop: c.pa.mainloop_run(loop, self._ret)

	def _pulse_iterate(self, block=True):
		with self._pulse_loop() as loop: c.pa.mainloop_iterate(loop, int(block), self._ret)

	@contextmanager
	def _pulse_op_cb(self, raw=False):
		act_id = next(self._action_ids)
		self._actions[act_id] = None
		try:
			cb = lambda s=True,k=act_id: self._actions.update({k: bool(s)})
			if not raw: cb = c.PA_CONTEXT_SUCCESS_CB_T(lambda ctx,s,d,cb=cb: cb(s))
			yield cb
			while self._actions[act_id] is None: self._pulse_iterate()
			if not self._actions[act_id]: raise PulseOperationFailed(act_id)
		finally: self._actions.pop(act_id, None)

	def _pulse_poll(self, timeout=None):
		'''timeout should be in seconds (float),
			0 for non-blocking poll and None (default) for no timeout.'''
		with self._pulse_loop() as loop:
			ts = c.mono_time()
			ts_deadline = timeout and (ts + timeout)
			while True:
				delay = max(0, int((ts_deadline - ts) * 1000000)) if ts_deadline else -1
				c.pa.mainloop_prepare(loop, delay) # usec
				c.pa.mainloop_poll(loop)
				if self._loop_closed: break # interrupted by close() or such
				c.pa.mainloop_dispatch(loop)
				if self._loop_stop: break
				ts = c.mono_time()
				if ts_deadline and ts >= ts_deadline: break


	def _pulse_info_cb(self, info_cls, data_list, done_cb, ctx, info, eof, userdata):
		if eof: done_cb()
		else: data_list.append(info_cls(info[0]))
		return 0

	def _pulse_get_list(cb_t, pulse_func, info_cls, singleton=False, index_arg=True):
		def _wrapper(self, index=None):
			data = list()
			with self._pulse_op_cb(raw=True) as cb:
				cb = cb_t(
					ft.partial(self._pulse_info_cb, info_cls, data, cb) if not singleton else
					lambda ctx, info, userdata, cb=cb: data.append(info_cls(info[0])) or cb() )
				pulse_func(self._ctx, *([index, cb, None] if index is not None else [cb, None]))
			data = data or list()
			if index is not None or singleton:
				if not data: raise PulseIndexError(index)
				data, = data
			return _wrapper.func(self, data) if _wrapper.func else data
		_wrapper.func = None
		def _add_wrap_doc(func):
			func.__name__ = '...'
			func.__doc__ = 'Signature: func({})'.format(
				'' if pulse_func.__name__.endswith('_list') or singleton or not index_arg else 'index' )
		def _decorator_or_method(func_or_self=None, index=None):
			if func_or_self.__class__.__name__ == 'Pulse':
				return _wrapper(func_or_self, index)
			elif func_or_self: _wrapper.func = func_or_self
			assert index is None, index
			return _wrapper
		_add_wrap_doc(_wrapper)
		_add_wrap_doc(_decorator_or_method)
		return _decorator_or_method

	sink_input_list = _pulse_get_list(
		c.PA_SINK_INPUT_INFO_CB_T,
		c.pa.context_get_sink_input_info_list, PulseSinkInputInfo )
	sink_input_info = _pulse_get_list(
		c.PA_SINK_INPUT_INFO_CB_T,
		c.pa.context_get_sink_input_info, PulseSinkInputInfo )
	source_output_list = _pulse_get_list(
		c.PA_SOURCE_OUTPUT_INFO_CB_T,
		c.pa.context_get_source_output_info_list, PulseSourceOutputInfo )
	source_output_info = _pulse_get_list(
		c.PA_SOURCE_OUTPUT_INFO_CB_T,
		c.pa.context_get_source_output_info, PulseSourceOutputInfo )

	sink_list = _pulse_get_list(
		c.PA_SINK_INFO_CB_T, c.pa.context_get_sink_info_list, PulseSinkInfo )
	sink_info = _pulse_get_list(
		c.PA_SINK_INFO_CB_T, c.pa.context_get_sink_info_by_index, PulseSinkInfo )
	source_list = _pulse_get_list(
		c.PA_SOURCE_INFO_CB_T, c.pa.context_get_source_info_list, PulseSourceInfo )
	source_info = _pulse_get_list(
		c.PA_SOURCE_INFO_CB_T, c.pa.context_get_source_info_by_index, PulseSourceInfo )
	card_list = _pulse_get_list(
		c.PA_CARD_INFO_CB_T, c.pa.context_get_card_info_list, PulseCardInfo )
	card_info = _pulse_get_list(
		c.PA_CARD_INFO_CB_T, c.pa.context_get_card_info_by_index, PulseCardInfo )
	client_list = _pulse_get_list(
		c.PA_CLIENT_INFO_CB_T, c.pa.context_get_client_info_list, PulseClientInfo )
	client_info = _pulse_get_list(
		c.PA_CLIENT_INFO_CB_T, c.pa.context_get_client_info, PulseClientInfo )
	server_info = _pulse_get_list(
		c.PA_SERVER_INFO_CB_T, c.pa.context_get_server_info, PulseServerInfo, singleton=True )
	module_info = _pulse_get_list(
		c.PA_MODULE_INFO_CB_T, c.pa.context_get_module_info, PulseModuleInfo )
	module_list = _pulse_get_list(
		c.PA_MODULE_INFO_CB_T, c.pa.context_get_module_info_list, PulseModuleInfo )


	def _pulse_method_call(pulse_op, func=None, index_arg=True):
		'''Creates following synchronous wrapper for async pa_operation callable:
			wrapper(index, ...) -> pulse_op(index, [*]args_func(...))
			index_arg=False: wrapper(...) -> pulse_op([*]args_func(...))'''
		def _wrapper(self, *args, **kws):
			if index_arg:
				if 'index' in kws: index = kws.pop('index')
				else: index, args = args[0], args[1:]
			pulse_args = func(*args, **kws) if func else list()
			if not is_list(pulse_args): pulse_args = [pulse_args]
			if index_arg: pulse_args = [index] + list(pulse_args)
			with self._pulse_op_cb() as cb:
				try: pulse_op(self._ctx, *(list(pulse_args) + [cb, None]))
				except c.ArgumentError as err: raise TypeError(err.args)
				except c.pa.CallError as err: raise PulseOperationInvalid(err.args[-1])
		func_args = list(inspect.getargspec(func or (lambda: None)))
		func_args[0] = list(func_args[0])
		if index_arg: func_args[0] = ['index'] + func_args[0]
		_wrapper.__name__ = '...'
		_wrapper.__doc__ = 'Signature: func' + inspect.formatargspec(*func_args)
		if func.__doc__: _wrapper.__doc__ += '\n\n' + func.__doc__
		return _wrapper

	card_profile_set_by_index = _pulse_method_call(
		c.pa.context_set_card_profile_by_index, lambda profile_name: profile_name )

	sink_default_set = _pulse_method_call(
		c.pa.context_set_default_sink, index_arg=False,
		func=lambda sink: sink.name if isinstance(sink, PulseSinkInfo) else sink )
	source_default_set = _pulse_method_call(
		c.pa.context_set_default_source, index_arg=False,
		func=lambda source: source.name if isinstance(source, PulseSourceInfo) else source )

	sink_input_mute = _pulse_method_call(
		c.pa.context_set_sink_input_mute, lambda mute=True: mute )
	sink_input_move = _pulse_method_call(
		c.pa.context_move_sink_input_by_index, lambda sink_index: sink_index )
	sink_mute = _pulse_method_call(
		c.pa.context_set_sink_mute_by_index, lambda mute=True: mute )
	sink_input_volume_set = _pulse_method_call(
		c.pa.context_set_sink_input_volume, lambda vol: vol.to_struct() )
	sink_volume_set = _pulse_method_call(
		c.pa.context_set_sink_volume_by_index, lambda vol: vol.to_struct() )
	sink_suspend = _pulse_method_call(
		c.pa.context_suspend_sink_by_index, lambda suspend=True: suspend )
	sink_port_set = _pulse_method_call(
		c.pa.context_set_sink_port_by_index,
		lambda port: port.name if isinstance(port, PulsePortInfo) else port )

	source_output_mute = _pulse_method_call(
		c.pa.context_set_source_output_mute, lambda mute=True: mute )
	source_output_move = _pulse_method_call(
		c.pa.context_move_source_output_by_index, lambda sink_index: sink_index )
	source_mute = _pulse_method_call(
		c.pa.context_set_source_mute_by_index, lambda mute=True: mute )
	source_output_volume_set = _pulse_method_call(
		c.pa.context_set_source_output_volume, lambda vol: vol.to_struct() )
	source_volume_set = _pulse_method_call(
		c.pa.context_set_source_volume_by_index, lambda vol: vol.to_struct() )
	source_suspend = _pulse_method_call(
		c.pa.context_suspend_source_by_index, lambda suspend=True: suspend )
	source_port_set = _pulse_method_call(
		c.pa.context_set_source_port_by_index,
		lambda port: port.name if isinstance(port, PulsePortInfo) else port )


	def module_load(self, name, args=''):
		if is_list(args): args = ' '.join(args)
		name, args = map(c.force_bytes, [name, args])
		data = list()
		with self._pulse_op_cb(raw=True) as cb:
			cb = c.PA_CONTEXT_INDEX_CB_T(
				lambda ctx, index, userdata, cb=cb: data.append(index) or cb() )
			try: c.pa.context_load_module(self._ctx, name, args, cb, None)
			except c.pa.CallError as err: raise PulseOperationInvalid(err.args[-1])
		index, = data
		return index

	module_unload = _pulse_method_call(c.pa.context_unload_module, None)


	def stream_restore_test(self):
		'Returns module-stream-restore version int (e.g. 1) or None if it is unavailable.'
		data = list()
		with self._pulse_op_cb(raw=True) as cb:
			cb = c.PA_EXT_STREAM_RESTORE_TEST_CB_T(
				lambda ctx, version, userdata, cb=cb: data.append(version) or cb() )
			try: c.pa.ext_stream_restore_test(self._ctx, cb, None)
			except c.pa.CallError as err: raise PulseOperationInvalid(err.args[-1])
		version, = data
		return version if version != c.PA_INVALID else None

	stream_restore_read = _pulse_get_list(
		c.PA_EXT_STREAM_RESTORE_READ_CB_T,
		c.pa.ext_stream_restore_read, PulseExtStreamRestoreInfo, index_arg=False )
	stream_restore_list = stream_restore_read # for consistency with other *_list methods

	@ft.partial(_pulse_method_call, c.pa.ext_stream_restore_write, index_arg=False)
	def stream_restore_write( obj_name_or_list,
			mode='merge', apply_immediately=False, **obj_kws ):
		'''Update module-stream-restore db entry for specified name.
			Can be passed PulseExtStreamRestoreInfo object or list of them as argument,
				or name string there and object init keywords (e.g. volume, mute, channel_list, etc).
			"mode" is PulseUpdateEnum value of
				'merge' (default), 'replace' or 'set' (replaces ALL entries!!!).'''
		mode = PulseUpdateEnum[mode]._c_val
		if is_str(obj_name_or_list):
			obj_name_or_list = PulseExtStreamRestoreInfo(obj_name_or_list, **obj_kws)
		if isinstance(obj_name_or_list, PulseExtStreamRestoreInfo):
			obj_name_or_list = [obj_name_or_list]
		# obj_array is an array of structs, laid out contiguously in memory, not pointers
		obj_array = (c.PA_EXT_STREAM_RESTORE_INFO * len(obj_name_or_list))()
		for n, obj in enumerate(obj_name_or_list):
			obj_struct, dst_struct = obj.to_struct(), obj_array[n]
			for k,t in obj_struct._fields_: setattr(dst_struct, k, getattr(obj_struct, k))
		return mode, obj_array, len(obj_array), int(bool(apply_immediately))

	@ft.partial(_pulse_method_call, c.pa.ext_stream_restore_delete, index_arg=False)
	def stream_restore_delete(obj_name_or_list):
		'''Can be passed string name,
			PulseExtStreamRestoreInfo object or a list of any of these.'''
		if is_str(obj_name_or_list, PulseExtStreamRestoreInfo):
			obj_name_or_list = [obj_name_or_list]
		name_list = list((obj.name if isinstance( obj,
			PulseExtStreamRestoreInfo ) else obj) for obj in obj_name_or_list)
		name_struct = (c.c_char_p * len(name_list))()
		name_struct[:] = list(map(c.force_bytes, name_list))
		return [name_struct]


	def default_set(self, obj):
		'Set passed sink or source to be used as default one by pulseaudio server.'
		assert_pulse_object(obj)
		method = {
			PulseSinkInfo: self.sink_default_set,
			PulseSourceInfo: self.source_default_set }.get(type(obj))
		if not method: raise NotImplementedError(type(obj))
		method(obj)

	def mute(self, obj, mute=True):
		assert_pulse_object(obj)
		method = {
			PulseSinkInfo: self.sink_mute,
			PulseSinkInputInfo: self.sink_input_mute,
			PulseSourceInfo: self.source_mute,
			PulseSourceOutputInfo: self.source_output_mute }.get(type(obj))
		if not method: raise NotImplementedError(type(obj))
		method(obj.index, mute)
		obj.mute = mute

	def port_set(self, obj, port):
		assert_pulse_object(obj)
		method = {
			PulseSinkInfo: self.sink_port_set,
			PulseSourceInfo: self.source_port_set }.get(type(obj))
		if not method: raise NotImplementedError(type(obj))
		method(obj.index, port)
		obj.port_active = port

	def card_profile_set(self, card, profile):
		assert_pulse_object(card)
		if is_str(profile):
			profile_dict = dict((p.name, p) for p in card.profile_list)
			if profile not in profile_dict:
				raise PulseIndexError( 'Card does not have'
					' profile with specified name: {!r}'.format(profile) )
			profile = profile_dict[profile]
		self.card_profile_set_by_index(card.index, profile.name)
		card.profile_active = profile

	def volume_set(self, obj, vol):
		assert_pulse_object(obj)
		method = {
			PulseSinkInfo: self.sink_volume_set,
			PulseSinkInputInfo: self.sink_input_volume_set,
			PulseSourceInfo: self.source_volume_set,
			PulseSourceOutputInfo: self.source_output_volume_set }.get(type(obj))
		if not method: raise NotImplementedError(type(obj))
		method(obj.index, vol)
		obj.volume = vol

	def volume_set_all_chans(self, obj, vol):
		assert_pulse_object(obj)
		obj.volume.value_flat = vol
		self.volume_set(obj, obj.volume)

	def volume_change_all_chans(self, obj, inc):
		assert_pulse_object(obj)
		obj.volume.values = [max(0, v + inc) for v in obj.volume.values]
		self.volume_set(obj, obj.volume)

	def volume_get_all_chans(self, obj):
		assert_pulse_object(obj)
		return obj.volume.value_flat


	def event_mask_set(self, *masks):
		mask = 0
		for m in masks: mask |= PulseEventMaskEnum[m]._c_val
		with self._pulse_op_cb() as cb:
			c.pa.context_subscribe(self._ctx, mask, cb, None)

	def event_callback_set(self, func):
		'''Call event_listen() to start receiving these,
				and be sure to raise PulseLoopStop in a callback to stop the loop.
			Passing None will disable the thing.'''
		self.event_callback = func

	def event_listen(self, timeout=None, raise_on_disconnect=True):
		'''Does not return until PulseLoopStop
				gets raised in event callback or timeout passes.
			timeout should be in seconds (float),
				0 for non-blocking poll and None (default) for no timeout.
			raise_on_disconnect causes PulseDisconnected exceptions by default.
			Do not run any pulse operations from these callbacks.'''
		assert self.event_callback
		try: self._pulse_poll(timeout)
		except c.pa.CallError: pass # e.g. from mainloop_dispatch() on disconnect
		if raise_on_disconnect and not self.connected: raise PulseDisconnected()

	def event_listen_stop(self):
		'''Stop event_listen() loop from e.g. another thread.
			Does nothing if libpulse poll is not running yet, so might be racey with
				event_listen() - be sure to call it in a loop until event_listen returns or something.'''
		self._loop_stop = True
		c.pa.mainloop_wakeup(self._loop)


	def set_poll_func(self, func, func_err_handler=None):
		'''Can be used to integrate pulse client into existing eventloop.
			Function will be passed a list of pollfd structs and timeout value (seconds, float),
				which it is responsible to use and modify (set poll flags) accordingly,
				returning int value >= 0 with number of fds that had any new events within timeout.
			func_err_handler defaults to traceback.print_exception(),
				and will be called on any exceptions from callback (to e.g. log these),
				returning poll error code (-1) to libpulse after that.'''
		if not func_err_handler: func_err_handler = traceback.print_exception
		self._pa_poll_cb = c.PA_POLL_FUNC_T(ft.partial(self._pulse_poll_cb, func, func_err_handler))
		c.pa.mainloop_set_poll_func(self._loop, self._pa_poll_cb, None)


def connect_to_cli(server=None, as_file=True, socket_timeout=1.0, attempts=5, retry_delay=0.3):
	'''Returns connected CLI interface socket (as file object, unless as_file=False),
			where one can send same commands (as lines) as to "pacmd" tool
			or pulseaudio startup files (e.g. "default.pa").
		"server" option can be specified to use non-standard unix socket path
			(when passed absolute path string) or remote tcp socket,
			when passed remote host address (to use default port) or (host, port) tuple.
		Be sure to adjust "socket_timeout" option for tcp sockets over laggy internet.
		Returned file object has line-buffered output,
			so there should be no need to use flush() after every command.
		Be sure to read from the socket line-by-line until
			"### EOF" or timeout for commands that have output (e.g. "dump\\n").
		If default server socket is used (i.e. not specified),
			server pid will be signaled to load module-cli between connection attempts.
		Completely separate protocol from the regular API, as wrapped by libpulse.
		PulseError is raised on any failure.'''
	import socket, errno, signal, time
	s, n = None, attempts if attempts > 0 else None
	try:
		pid_path, sock_af, sock_t = None, socket.AF_UNIX, socket.SOCK_STREAM
		if not server: server, pid_path = map(c.pa.runtime_path, ['cli', 'pid'])
		else:
			if not is_list(server):
				server = c.force_str(server)
				if not server.startswith('/'): server = server, 4712 # default port
			if is_list(server):
				try:
					addrinfo = socket.getaddrinfo(
						server[0], server[1], 0, sock_t, socket.IPPROTO_TCP )
					if not addrinfo: raise socket.gaierror('No addrinfo for socket: {}'.format(server))
				except (socket.gaierror, socket.error) as err:
					raise PulseError( 'Failed to resolve socket parameters'
						' (address, family) via getaddrinfo: {!r} - {} {}'.format(server, type(err), err) )
				sock_af, sock_t, _, _, server = addrinfo[0]

		s = socket.socket(sock_af, sock_t)
		s.settimeout(socket_timeout)
		while True:
			ts = c.mono_time()
			try: s.connect(server)
			except socket.error as err:
				if err.errno not in [errno.ECONNREFUSED, errno.ENOENT, errno.ECONNABORTED]: raise
			else: break
			if n:
				n -= 1
				if n <= 0: raise PulseError('Number of connection attempts ({}) exceeded'.format(attempts))
			if pid_path:
				with open(pid_path) as src: os.kill(int(src.read().strip()), signal.SIGUSR2)
			time.sleep(max(0, retry_delay - (c.mono_time() - ts)))

		return s.makefile('rw', 1) if as_file else s

	except Exception as err: # CallError, socket.error, IOError (pidfile), OSError (os.kill)
		raise PulseError( 'Failed to connect to pulse'
			' cli socket {!r}: {} {}'.format(server, type(err), err) )

	finally:
		if s: s.close()
