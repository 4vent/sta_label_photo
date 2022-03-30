# -*- coding: utf-8 -*-

import console
yesOrNo = console.alert('ファイルが存在します。', '上書きしますか？', 'はい', 'いいえ', hide_cancel_button=True)
console.hud_alert(str(yesOrNo))
