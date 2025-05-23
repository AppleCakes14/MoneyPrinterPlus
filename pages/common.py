'''
Author: chenpeng 115522593@qq.com
Date: 2025-01-22 10:04:50
LastEditors: chenpeng 115522593@qq.com
LastEditTime: 2025-01-24 14:00:57
FilePath: /MoneyPrinterPlus/pages/common.py
Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
'''
#  Copyright © [2024] 程序那些事
#
#  All rights reserved. This software and associated documentation files (the "Software") are provided for personal and educational use only. Commercial use of the Software is strictly prohibited unless explicit permission is obtained from the author.
#
#  Permission is hereby granted to any person to use, copy, and modify the Software for non-commercial purposes, provided that the following conditions are met:
#
#  1. The original copyright notice and this permission notice must be included in all copies or substantial portions of the Software.
#  2. Modifications, if any, must retain the original copyright information and must not imply that the modified version is an official version of the Software.
#  3. Any distribution of the Software or its modifications must retain the original copyright notice and include this permission notice.
#
#  For commercial use, including but not limited to selling, distributing, or using the Software as part of any commercial product or service, you must obtain explicit authorization from the author.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHOR OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
#  Author: 程序那些事
#  email: flydean@163.com
#  Website: [www.flydean.com](http://www.flydean.com)
#  GitHub: [https://github.com/ddean2009/MoneyPrinterPlus](https://github.com/ddean2009/MoneyPrinterPlus)
#
#  All rights reserved.
#
#

import streamlit as st

from tools.tr_utils import tr
from config.config import my_config

def common_ui():
    initialize_language()
    st.set_page_config(page_title="Video Generator Tools",
                       page_icon=":pretzel:",
                       layout="wide",
                       initial_sidebar_state="auto",
                       menu_items={
                           'Report a Bug': "https://github.com/ddean2009/MoneyPrinterPlus",
                           'About': "这是一个轻松搞钱的项目,关注我,带你搞钱",
                           'Get help': "https://www.flydean.com"
                       })

    st.sidebar.page_link("gui.py", label=tr("Base Config"))
    st.sidebar.page_link("pages/01_auto_video.py", label=tr("Generate Video"))
    st.sidebar.page_link("pages/02_mix_video.py", label=tr("Mix Video"))
    st.sidebar.page_link("pages/03_merge_video.py", label=tr("Merge Video"))
    st.sidebar.page_link("pages/04_auto_publish.py", label=tr("Video Auto Publish"))
    # st.sidebar.markdown("---")
    # st.sidebar.markdown(
    #     '<a style="text-align: center;padding-top: 0rem;" href="http://www.flydean.com">Developed by 程序那些事</a>',
    #     unsafe_allow_html=True)

    with st.sidebar:
        st.markdown('---')

def initialize_language():
    if 'ui_language_code' not in st.session_state:
        st.session_state['ui_language_code'] = my_config['ui']['language']
    else:
        # Make sure config always reflects session state
        my_config['ui']['language'] = st.session_state['ui_language_code']