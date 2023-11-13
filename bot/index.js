/**
 * 오픈채팅방에서 링크를 보내면, Lambda로 링크를 보내주는 메신저봇R JS 스크립트입니다.
 */

const scriptName = "개발이하고싶어";

const { Jsoup: Jsoup } = org.jsoup;
const API_URL = "https://gaebari.junah.dev/new_link";

/**
 * (string) room
 * (string) sender
 * (boolean) isGroupChat
 * (void) replier.reply(message)
 * (boolean) replier.reply(room, message, hideErrorToast = false) // 전송 성공시 true, 실패시 false 반환
 * (string) imageDB.getProfileBase64()
 * (string) packageName
 */
function responseFix(
  room,
  msg,
  sender,
  isGroupChat,
  replier,
  ImageDB,
  packageName
) {
  if (room != "개발이하고싶어") return;

  const regex = /https?:\/\/[^\s/$.?#].[^\s]*/g;
  const links = msg.match(regex) || [];

  for (let i = 0; i < links.length; i++) {
    const link = links[i];
    Jsoup.connect(API_URL)
      .header("Content-Type", "application/json")
      .requestBody(
        JSON.stringify({
          link: link,
          author: sender,
          created_at: new Date().toISOString(),
        })
      )
      .ignoreContentType(true)
      .ignoreHttpErrors(true)
      .timeout(10000)
      .post();
    Log.i("link: " + link + ", 보낸 사람: " + sender);
  }
}

/**
 * https://cafe.naver.com/msgbot/2067
 */
function onNotificationPosted(sbn, sm) {
  var packageName = sbn.getPackageName();
  if (!packageName.startsWith("com.kakao.tal")) return;
  var actions = sbn.getNotification().actions;
  if (actions == null) return;
  var userId = sbn.getUser().hashCode();
  for (var n = 0; n < actions.length; n++) {
    var action = actions[n];
    if (action.getRemoteInputs() == null) continue;
    var bundle = sbn.getNotification().extras;

    var msg = bundle.get("android.text").toString();
    var sender = bundle.getString("android.title");
    var room = bundle.getString("android.subText");
    if (room == null) room = bundle.getString("android.summaryText");
    var isGroupChat = room != null;
    if (room == null) room = sender;
    var replier = new com.xfl.msgbot.script.api.legacy.SessionCacheReplier(
      packageName,
      action,
      room,
      false,
      ""
    );
    var icon = bundle
      .getParcelableArray("android.messages")[0]
      .get("sender_person")
      .getIcon()
      .getBitmap();
    var image = bundle.getBundle("android.wearable.EXTENSIONS");
    if (image != null) image = image.getParcelable("background");
    var imageDB = new com.xfl.msgbot.script.api.legacy.ImageDB(icon, image);
    com.xfl.msgbot.application.service.NotificationListener.Companion.setSession(
      packageName,
      room,
      action
    );
    if (this.hasOwnProperty("responseFix")) {
      responseFix(
        room,
        msg,
        sender,
        isGroupChat,
        replier,
        imageDB,
        packageName,
        userId != 0
      );
    }
  }
}
