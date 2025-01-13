# GloFlow application and media management/publishing platform
# Copyright (C) 2019 Ivan Trajkovic
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import traceback
import sentry_sdk

#--------------------------------------------------------
def create(p_msg_str,
	p_type_str,
	p_data_map,
	p_exception,
	p_sybsystem_name_str,
	p_log_fun,
	p_sentry_bool=True,
	p_reraise_bool=False):
	assert isinstance(p_exception, Exception)
	assert isinstance(p_data_map, dict) or p_data_map == None
	
	full_msg_str = f'''
		{p_msg_str}
		{p_sybsystem_name_str}
		exception args: {p_exception.args}
		exception msg: {p_exception.message}
		trace: {traceback.format_exc()}
	'''

	if p_sentry_bool:
		sentry_sdk.capture_exception(p_exception)
	
	p_log_fun('ERROR', full_msg_str)

	if p_reraise_bool:
		raise p_exception