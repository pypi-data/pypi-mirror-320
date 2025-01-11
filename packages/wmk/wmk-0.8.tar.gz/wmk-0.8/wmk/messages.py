# Automatically generated file from a JSON schema


from typing import Any, Literal, Required, TypedDict, Union


class ActionElementEvent(TypedDict, total=False):
    """ ActionElementEvent. """

    type: Required[Literal['ActionElementEvent']]
    """ Required property """

    actionElementId: Required[str]
    """ Required property """

    value: str
    event: Required["_ActionElementEventevent"]
    """ Required property """



class ActionElementStatus(TypedDict, total=False):
    """ ActionElementStatus. """

    type: Required[Literal['ActionElementStatus']]
    """ Required property """

    actionElementId: Required[str]
    """ Required property """

    value: Required[str]
    """ Required property """

    hidden: bool
    options: "_ActionElementStatusoptions"


class ActionElementsInfo(TypedDict, total=False):
    """ ActionElementsInfo. """

    type: Required[Literal['ActionElementsInfo']]
    """ Required property """

    elements: Required[list["_ActionElementsInfoelementsitem"]]
    """ Required property """



class ActionPanel(TypedDict, total=False):
    """
    ActionPanel.

    deprecated: True
    """

    type: Required[Literal['ActionPanel']]
    """ Required property """

    display: Required[bool]
    """ Required property """

    id: Required[str]
    """ Required property """



class ActivateMovementType(TypedDict, total=False):
    """ ActivateMovementType. """

    type: Required[Literal['ActivateMovementType']]
    """ Required property """

    movementType: Required["_ActivateMovementTypemovementType"]
    """ Required property """



class ActiveRegion(TypedDict, total=False):
    """ ActiveRegion. """

    type: Required[Literal['ActiveRegion']]
    """ Required property """

    regionId: Required[str]
    """ Required property """

    categoryId: str


class AnalyticsEvent(TypedDict, total=False):
    """ AnalyticsEvent. """

    type: Required[Literal['AnalyticsEvent']]
    """ Required property """

    eventName: Required[str]
    """ Required property """



class BusinessCard(TypedDict, total=False):
    """
    BusinessCard.

    deprecated: True
    """

    type: Required[Literal['BusinessCard']]
    """ Required property """

    firstName: Required[str]
    """ Required property """

    lastName: Required[str]
    """ Required property """

    email: Required[str]
    """ Required property """

    city: Required[str]
    """ Required property """

    avatarColor: Required["GameColor8681"]
    """
    GameColor.

    Required property
    """

    avatarId: Required[str]
    """ Required property """

    customAvatarUrl: Required[str]
    """ Required property """

    customAvatarPreviewImgUrl: Required[str]
    """ Required property """

    company: Required[str]
    """ Required property """

    orgCode: Required[str]
    """ Required property """

    country: Required[str]
    """ Required property """

    website: Required[str]
    """ Required property """

    twitter: Required[str]
    """ Required property """

    xing: Required[str]
    """ Required property """

    instagram: Required[str]
    """ Required property """

    linkedin: Required[str]
    """ Required property """

    facebook: Required[str]
    """ Required property """

    userEmail: Required[str]
    """ Required property """

    msTeamsEmail: Required[str]
    """ Required property """

    guestEmail: Required[str]
    """ Required property """

    age: Required[int | float]
    """ Required property """

    environment: Required[str]
    """ Required property """

    jobTitle: Required[str]
    """ Required property """

    playerId: Required[int | float]
    """ Required property """

    roomId: Required[str]
    """ Required property """



class ClientInfo(TypedDict, total=False):
    """ ClientInfo. """

    type: Required[Literal['ClientInfo']]
    """ Required property """

    isTouchDevice: Required[bool]
    """ Required property """

    langCode: str
    userAgent: str
    webBackgroundColor: str
    webTextColor: str


class CurrencyChanged(TypedDict, total=False):
    """ CurrencyChanged. """

    type: Required[Literal['CurrencyChanged']]
    """ Required property """

    currencyId: Required[str]
    """ Required property """

    delta: Required[int | float]
    """ Required property """

    newAmount: Required[int | float]
    """ Required property """



class CustomMessage(TypedDict, total=False):
    """ CustomMessage. """

    type: Required[Literal['CustomMessage']]
    """ Required property """

    messageType: Required[str]
    """ Required property """

    data: Required[dict[str, Any]]
    """ Required property """



class CustomMessage836(TypedDict, total=False):
    """ CustomMessage. """

    type: Required[Literal['CustomMessage']]
    """ Required property """

    messageType: Required[str]
    """ Required property """

    data: Required[dict[str, Any]]
    """ Required property """



class DeleteMessage(TypedDict, total=False):
    """ DeleteMessage. """

    type: Required[Literal['DeleteMessage']]
    """ Required property """

    userId: Required[int | float]
    """ Required property """

    messageId: Required[int | float]
    """ Required property """



class DidFakeTouch(TypedDict, total=False):
    """ DidFakeTouch. """

    type: Required[Literal['DidFakeTouch']]
    """ Required property """



class DisplayMap(TypedDict, total=False):
    """
    DisplayMap.

    deprecated: True
    """

    type: Required[Literal['DisplayMap']]
    """ Required property """

    display: Required[bool]
    """ Required property """



class EditingBusinessCard(TypedDict, total=False):
    """
    EditingBusinessCard.

    deprecated: True
    """

    type: Required[Literal['EditingBusinessCard']]
    """ Required property """

    opened: Required[bool]
    """ Required property """



class EndSession(TypedDict, total=False):
    """ EndSession. """

    type: Required[Literal['EndSession']]
    """ Required property """



class EnterRegion(TypedDict, total=False):
    """ EnterRegion. """

    type: Required[Literal['EnterRegion']]
    """ Required property """

    regionId: Required[str]
    """ Required property """



class ExitRegion(TypedDict, total=False):
    """ ExitRegion. """

    type: Required[Literal['ExitRegion']]
    """ Required property """

    regionId: Required[str]
    """ Required property """



class ExternalAssetLoadStatus(TypedDict, total=False):
    """ ExternalAssetLoadStatus. """

    type: Required[Literal['ExternalAssetLoadStatus']]
    """ Required property """

    target: Required[str]
    """ Required property """

    status: Required[str]
    """ Required property """

    description: str
    uri: Required[str]
    """ Required property """



class GameColor(TypedDict, total=False):
    """ GameColor. """

    r: Required[int | float]
    """
    minimum: 0
    maximum: 255

    Required property
    """

    g: Required[int | float]
    """
    minimum: 0
    maximum: 255

    Required property
    """

    b: Required[int | float]
    """
    minimum: 0
    maximum: 255

    Required property
    """

    a: Required[int | float]
    """
    minimum: 0
    maximum: 255

    Required property
    """



class GameColor6313(TypedDict, total=False):
    """ GameColor. """

    r: Required[int | float]
    """
    minimum: 0
    maximum: 255

    Required property
    """

    g: Required[int | float]
    """
    minimum: 0
    maximum: 255

    Required property
    """

    b: Required[int | float]
    """
    minimum: 0
    maximum: 255

    Required property
    """

    a: Required[int | float]
    """
    minimum: 0
    maximum: 255

    Required property
    """



class GameColor8681(TypedDict, total=False):
    """ GameColor. """

    r: Required[int | float]
    """
    minimum: 0
    maximum: 255

    Required property
    """

    g: Required[int | float]
    """
    minimum: 0
    maximum: 255

    Required property
    """

    b: Required[int | float]
    """
    minimum: 0
    maximum: 255

    Required property
    """

    a: Required[int | float]
    """
    minimum: 0
    maximum: 255

    Required property
    """



class GameIsReady(TypedDict, total=False):
    """ GameIsReady. """

    type: Required[Literal['GameIsReady']]
    """ Required property """



class GameQuiz(TypedDict, total=False):
    """ GameQuiz. """

    type: Required[Literal['GameQuiz']]
    """ Required property """

    id: Required[str]
    """ Required property """

    answer: Required[str]
    """ Required property """



class GetScreenSharingStatus(TypedDict, total=False):
    """ GetScreenSharingStatus. """

    type: Required[Literal['GetScreenSharingStatus']]
    """ Required property """

    broadcast: Required[Literal[True]]
    """ Required property """



class GetScreenSharingStatus6532(TypedDict, total=False):
    """ GetScreenSharingStatus. """

    type: Required[Literal['GetScreenSharingStatus']]
    """ Required property """

    broadcast: Required[Literal[True]]
    """ Required property """



class HideUi(TypedDict, total=False):
    """
    HideUi.

    deprecated: True
    """

    type: Required[Literal['HideUi']]
    """ Required property """

    hide: Required[bool]
    """ Required property """



class InfoCard(TypedDict, total=False):
    """
    InfoCard.

    deprecated: True
    """

    type: Required[Literal['InfoCard']]
    """ Required property """

    display: Required[bool]
    """ Required property """

    id: Required[str]
    """ Required property """



class ItemAdded(TypedDict, total=False):
    """ ItemAdded. """

    type: Required[Literal['ItemAdded']]
    """ Required property """

    slug: Required[str]
    """ Required property """

    amount: Required[int | float]
    """ Required property """



class LanguageSelected(TypedDict, total=False):
    """ LanguageSelected. """

    type: Required[Literal['LanguageSelected']]
    """ Required property """

    langCode: Required[str]
    """ Required property """



class LoadExternalAsset(TypedDict, total=False):
    """ LoadExternalAsset. """

    type: Required[Literal['LoadExternalAsset']]
    """ Required property """

    uri: Required[str]
    """ Required property """

    provider: Required[str]
    """ Required property """

    intent: Required[str | dict[str, Any]]
    """ Required property """



class LoadingLevelEnd(TypedDict, total=False):
    """
    LoadingLevelEnd.

    deprecated: True
    """

    type: Required[Literal['LoadingLevelEnd']]
    """ Required property """

    levelId: Required[str]
    """ Required property """



class LoadingLevelStart(TypedDict, total=False):
    """
    LoadingLevelStart.

    deprecated: True
    """

    type: Required[Literal['LoadingLevelStart']]
    """ Required property """

    levelId: Required[str]
    """ Required property """



class MediaCaptureAction(TypedDict, total=False):
    """ MediaCaptureAction. """

    type: Required[Literal['MediaCaptureAction']]
    """ Required property """

    mediaType: Required["_MediaCaptureActionmediaType"]
    """ Required property """

    action: Required["_MediaCaptureActionaction"]
    """ Required property """



class MediaCaptureEvent(TypedDict, total=False):
    """ MediaCaptureEvent. """

    type: Required[Literal['MediaCaptureEvent']]
    """ Required property """

    mediaType: Required["_MediaCaptureEventmediaType"]
    """ Required property """

    event: Required["_MediaCaptureEventevent"]
    """ Required property """



class MouseEnterClickableSpot(TypedDict, total=False):
    """ MouseEnterClickableSpot. """

    type: Required[Literal['MouseEnterClickableSpot']]
    """ Required property """

    interactableType: Required[str]
    """ Required property """



class MouseExitClickableSpot(TypedDict, total=False):
    """ MouseExitClickableSpot. """

    type: Required[Literal['MouseExitClickableSpot']]
    """ Required property """

    interactableType: Required[str]
    """ Required property """



class MovementTypeChanged(TypedDict, total=False):
    """ MovementTypeChanged. """

    type: Required[Literal['MovementTypeChanged']]
    """ Required property """

    movementType: Required["_MovementTypeChangedmovementType"]
    """ Required property """



class NearbyPlayer(TypedDict, total=False):
    """ NearbyPlayer. """

    playerId: Required[int | float]
    """ Required property """

    name: Required[str]
    """ Required property """

    distance: Required[int | float]
    """ Required property """

    avatarColor: Required["GameColor"]
    """
    GameColor.

    Required property
    """



class NearbyPlayers(TypedDict, total=False):
    """ NearbyPlayers. """

    type: Required[Literal['NearbyPlayers']]
    """ Required property """

    players: Required[list["NearbyPlayer"]]
    """ Required property """



class OnChatMessageDeleted(TypedDict, total=False):
    """ OnChatMessageDeleted. """

    type: Required[Literal['OnChatMessageDeleted']]
    """ Required property """

    senderId: Required[int | float]
    """ Required property """

    messageId: Required[int | float]
    """ Required property """



class OnStartAction(TypedDict, total=False):
    """ OnStartAction. """

    type: Required[Literal['OnStartAction']]
    """ Required property """



class OnStreamIsShown(TypedDict, total=False):
    """ OnStreamIsShown. """

    type: Required[Literal['OnStreamIsShown']]
    """ Required property """



class OpenBusinessCardEditor(TypedDict, total=False):
    """
    OpenBusinessCardEditor.

    deprecated: True
    """

    type: Required[Literal['OpenBusinessCardEditor']]
    """ Required property """



class PauseMode(TypedDict, total=False):
    """
    PauseMode.

    deprecated: True
    """

    type: Required[Literal['PauseMode']]
    """ Required property """

    pauseMode: Required[bool]
    """ Required property """



class PauseStream(TypedDict, total=False):
    """ PauseStream. """

    type: Required[Literal['PauseStream']]
    """ Required property """



class PerformanceStats(TypedDict, total=False):
    """ PerformanceStats. """

    type: Required[Literal['PerformanceStats']]
    """ Required property """

    cpuUsage: Required[int | float]
    """
    minimum: 0
    maximum: 100

    Required property
    """

    gpuUsage: Required[int | float]
    """
    minimum: 0
    maximum: 100

    Required property
    """

    fps: int | float


class PhotoCaptureEvent(TypedDict, total=False):
    """
    PhotoCaptureEvent.

    deprecated: True
    """

    type: Required[Literal['PhotoCaptureEvent']]
    """ Required property """

    event: Required["_PhotoCaptureEventevent"]
    """ Required property """



class PhotonPlayerConnected(TypedDict, total=False):
    """ PhotonPlayerConnected. """

    type: Required[Literal['PhotonPlayerConnected']]
    """ Required property """

    playerId: Required[int | float]
    """ Required property """

    roomId: Required[str]
    """ Required property """



class PhotonPlayerDisconnected(TypedDict, total=False):
    """ PhotonPlayerDisconnected. """

    type: Required[Literal['PhotonPlayerDisconnected']]
    """ Required property """



class Poll(TypedDict, total=False):
    """
    Poll.

    deprecated: True
    """

    type: Required[Literal['Poll']]
    """ Required property """

    display: Required[bool]
    """ Required property """

    id: Required[str]
    """ Required property """



class PollResultSubmitted(TypedDict, total=False):
    """ PollResultSubmitted. """

    type: Required[Literal['PollResultSubmitted']]
    """ Required property """

    slug: Required[str]
    """ Required property """

    userId: Required[str]
    """ Required property """

    entries: Required[str]
    """ Required property """



class ProductSelected(TypedDict, total=False):
    """ ProductSelected. """

    type: Required[Literal['ProductSelected']]
    """ Required property """

    slug: Required[str]
    """ Required property """

    variant: str


class QuestProgress(TypedDict, total=False):
    """ QuestProgress. """

    type: Required[Literal['QuestProgress']]
    """ Required property """

    quest: Required["_QuestProgressquest"]
    """ Required property """

    hasProgressUI: Required[bool]
    """ Required property """



class QuestsInfo(TypedDict, total=False):
    """ QuestsInfo. """

    type: Required[Literal['QuestsInfo']]
    """ Required property """

    quests: Required[list["_QuestsInfoquestsitem"]]
    """ Required property """



class Reaction(TypedDict, total=False):
    """ Reaction. """

    type: Required[Literal['Reaction']]
    """ Required property """

    reaction: Required[str]
    """ Required property """

    stage: int | float
    playerId: Required[int | float]
    """ Required property """

    roomId: Required[str]
    """ Required property """

    broadcast: Required[Literal[True]]
    """ Required property """



class Reaction1508(TypedDict, total=False):
    """ Reaction. """

    type: Required[Literal['Reaction']]
    """ Required property """

    reaction: Required[str]
    """ Required property """

    stage: int | float
    playerId: Required[int | float]
    """ Required property """

    roomId: Required[str]
    """ Required property """

    broadcast: Required[Literal[True]]
    """ Required property """



class ReceivedChatMessage(TypedDict, total=False):
    """ ReceivedChatMessage. """

    type: Required[Literal['ReceivedChatMessage']]
    """ Required property """

    content: Required[str]
    """ Required property """

    sender: Required[str]
    """ Required property """

    senderId: Required[int | float]
    """ Required property """

    channelId: str
    messageId: int | float
    roomId: Required[str]
    """ Required property """



class RequestQuestsInfo(TypedDict, total=False):
    """ RequestQuestsInfo. """

    type: Required[Literal['RequestQuestsInfo']]
    """ Required property """



class ResumeStream(TypedDict, total=False):
    """ ResumeStream. """

    type: Required[Literal['ResumeStream']]
    """ Required property """



class RoomTeleportEnd(TypedDict, total=False):
    """ RoomTeleportEnd. """

    type: Required[Literal['RoomTeleportEnd']]
    """ Required property """

    success: Required[bool]
    """ Required property """

    errorCode: Required[int | float]
    """ Required property """



class RoomTeleportStart(TypedDict, total=False):
    """ RoomTeleportStart. """

    type: Required[Literal['RoomTeleportStart']]
    """ Required property """



class ScreenSharing(TypedDict, total=False):
    """ ScreenSharing. """

    type: Required[Literal['ScreenSharing']]
    """ Required property """

    participantId: Required[str]
    """ Required property """

    isSharing: Required[bool]
    """ Required property """

    broadcast: Required[Literal[True]]
    """ Required property """



class ScreenSharing1587(TypedDict, total=False):
    """ ScreenSharing. """

    type: Required[Literal['ScreenSharing']]
    """ Required property """

    participantId: Required[str]
    """ Required property """

    isSharing: Required[bool]
    """ Required property """

    broadcast: Required[Literal[True]]
    """ Required property """



class ScreenSize(TypedDict, total=False):
    """ ScreenSize. """

    type: Required[Literal['ScreenSize']]
    """ Required property """

    w: Required[int | float]
    """ Required property """

    h: Required[int | float]
    """ Required property """

    croppedLeft: Required[int | float]
    """ Required property """

    croppedRight: Required[int | float]
    """ Required property """

    croppedTop: Required[int | float]
    """ Required property """

    croppedBottom: Required[int | float]
    """ Required property """



class SendChatMessage(TypedDict, total=False):
    """ SendChatMessage. """

    type: Required[Literal['SendChatMessage']]
    """ Required property """

    content: Required[str]
    """ Required property """



class SendEmoji(TypedDict, total=False):
    """ SendEmoji. """

    type: Required[Literal['SendEmoji']]
    """ Required property """

    emoji: Required[str]
    """ Required property """



class SetIsPresenter(TypedDict, total=False):
    """ SetIsPresenter. """

    type: Required[Literal['SetIsPresenter']]
    """ Required property """

    userId: str


class SetPointerScheme(TypedDict, total=False):
    """
    SetPointerScheme.

    deprecated: True
    """

    type: Required[Literal['SetPointerScheme']]
    """ Required property """

    scheme: Required["_SetPointerSchemescheme"]
    """ Required property """



class ShareMedia(TypedDict, total=False):
    """ ShareMedia. """

    type: Required[Literal['ShareMedia']]
    """ Required property """

    url: Required[str]
    """ Required property """

    mediaType: Required["_ShareMediamediaType"]
    """ Required property """

    endSession: Required[bool]
    """ Required property """

    onMobile: Required[bool]
    """ Required property """

    onDesktop: Required[bool]
    """ Required property """



class ShowBusinessCard(TypedDict, total=False):
    """ ShowBusinessCard. """

    type: Required[Literal['ShowBusinessCard']]
    """ Required property """

    firstName: Required[str]
    """ Required property """

    lastName: Required[str]
    """ Required property """

    email: Required[str]
    """ Required property """

    city: Required[str]
    """ Required property """

    avatarColor: Required["GameColor6313"]
    """
    GameColor.

    Required property
    """

    avatarId: Required[str]
    """ Required property """

    customAvatarUrl: Required[str]
    """ Required property """

    customAvatarPreviewImgUrl: Required[str]
    """ Required property """

    company: Required[str]
    """ Required property """

    orgCode: Required[str]
    """ Required property """

    country: Required[str]
    """ Required property """

    website: Required[str]
    """ Required property """

    twitter: Required[str]
    """ Required property """

    xing: Required[str]
    """ Required property """

    instagram: Required[str]
    """ Required property """

    linkedin: Required[str]
    """ Required property """

    facebook: Required[str]
    """ Required property """

    userEmail: Required[str]
    """ Required property """

    msTeamsEmail: Required[str]
    """ Required property """

    guestEmail: Required[str]
    """ Required property """

    age: Required[int | float]
    """ Required property """

    environment: Required[str]
    """ Required property """

    jobTitle: Required[str]
    """ Required property """

    playerId: Required[int | float]
    """ Required property """

    roomId: Required[str]
    """ Required property """



class SmartChatAction(TypedDict, total=False):
    """ SmartChatAction. """

    type: Required[Literal['SmartChatAction']]
    """ Required property """

    smartChatSlug: Required[str]
    """ Required property """

    action: Required["_SmartChatActionaction"]
    """ Required property """



class SmartChatEngineReply(TypedDict, total=False):
    """ SmartChatEngineReply. """

    type: Required[Literal['SmartChatEngineReply']]
    """ Required property """

    smartChatSlug: Required[str]
    """ Required property """

    message: Required[str]
    """ Required property """



class SmartChatSubscriptionUpdate(TypedDict, total=False):
    """ SmartChatSubscriptionUpdate. """

    type: Required[Literal['SmartChatSubscriptionUpdate']]
    """ Required property """

    smartChatSlugs: Required[list[str]]
    """ Required property """



class SmartChatUserAction(TypedDict, total=False):
    """ SmartChatUserAction. """

    type: Required[Literal['SmartChatUserAction']]
    """ Required property """

    smartChatSlug: Required[str]
    """ Required property """

    action: Required["_SmartChatUserActionaction"]
    """ Required property """



class SmartChatUserPrompt(TypedDict, total=False):
    """ SmartChatUserPrompt. """

    type: Required[Literal['SmartChatUserPrompt']]
    """ Required property """

    smartChatSlug: Required[str]
    """ Required property """

    message: Required[str]
    """ Required property """



class StreamingStats(TypedDict, total=False):
    """ StreamingStats. """

    id: Required[str]
    """ Required property """

    type: Required[str]
    """ Required property """

    isRemote: Required[bool]
    """ Required property """

    mediaType: Required[str]
    """ Required property """

    timestamp: Required[int | float]
    """ Required property """

    bytesReceived: Required[int | float]
    """ Required property """

    framesDecoded: Required[int | float]
    """ Required property """

    packetsLost: Required[int | float]
    """ Required property """

    jitter: Required[int | float]
    """ Required property """

    jitterBufferDelay: Required[int | float]
    """ Required property """

    jitterBufferEmittedCount: Required[int | float]
    """ Required property """

    jitterBufferDelayAvg: Required[int | float]
    """ Required property """

    totalDecodeTime: Required[int | float]
    """ Required property """

    totalInterFrameDelay: Required[int | float]
    """ Required property """

    totalProcessingDelay: Required[int | float]
    """ Required property """

    bytesReceivedStart: Required[int | float]
    """ Required property """

    timestampStart: Required[int | float]
    """ Required property """

    avgBitrate: Required[int | float]
    """ Required property """

    kind: Required[str]
    """ Required property """

    trackIdentifier: Required[str]
    """ Required property """

    bitrate: Required[int | float]
    """ Required property """

    lowBitrate: Required[int | float]
    """ Required property """

    highBitrate: Required[int | float]
    """ Required property """

    framesDecodedStart: Required[int | float]
    """ Required property """

    framesDroppedPercentage: Required[int | float]
    """ Required property """

    framerate: Required[int | float]
    """ Required property """

    avgframerate: Required[int | float]
    """ Required property """

    highFramerate: Required[int | float]
    """ Required property """

    lowFramerate: Required[int | float]
    """ Required property """

    framesDropped: Required[int | float]
    """ Required property """

    framesReceived: Required[int | float]
    """ Required property """

    frameHeight: Required[int | float]
    """ Required property """

    frameHeightStart: Required[int | float]
    """ Required property """

    frameWidth: Required[int | float]
    """ Required property """

    frameWidthStart: Required[int | float]
    """ Required property """

    sessionPacketsLost: Required[int | float]
    """ Required property """

    sessionPacketsReceived: Required[int | float]
    """ Required property """

    sessionFreezeCount: Required[int | float]
    """ Required property """

    sessionTotalFreezesDuration: Required[int | float]
    """ Required property """

    sessionAvgFreezesDuration: Required[int | float]
    """ Required property """

    sessionFreezedSpentTime: Required[int | float]
    """ Required property """

    sessionAvgProcessingDelay: Required[int | float]
    """ Required property """

    sessionAvgDecodingDelay: Required[int | float]
    """ Required property """

    currentRoundTripTime: Required[int | float]
    """ Required property """

    currentPacketLostPercent: Required[int | float]
    """ Required property """

    currentJitterBufferDelay: Required[int | float]
    """ Required property """

    currentFreezeCount: Required[int | float]
    """ Required property """

    currentFreezeDurationPercent: Required[int | float]
    """ Required property """

    currentProcessingDelay: Required[int | float]
    """ Required property """

    currentDecodeDelay: Required[int | float]
    """ Required property """



class TakeScreenshot(TypedDict, total=False):
    """ TakeScreenshot. """

    type: Required[Literal['TakeScreenshot']]
    """ Required property """



class TeleportPlayer(TypedDict, total=False):
    """ TeleportPlayer. """

    type: Required[Literal['TeleportPlayer']]
    """ Required property """

    spawnPoint: Required[int | float]
    """ Required property """



class TeleportTo(TypedDict, total=False):
    """ TeleportTo. """

    type: Required[Literal['TeleportTo']]
    """ Required property """

    playerId: Required[int | float]
    """ Required property """

    roomId: str


class TimeTravel(TypedDict, total=False):
    """ TimeTravel. """

    type: Required[Literal['TimeTravel']]
    """ Required property """

    date: Required[str]
    """ Required property """



class UIElementCoords(TypedDict, total=False):
    """ UIElementCoords. """

    type: Required[Literal['UIElementCoords']]
    """ Required property """

    id: Required[str]
    """ Required property """

    x: Required[int | float]
    """ Required property """

    y: Required[int | float]
    """ Required property """

    w: Required[int | float]
    """ Required property """

    h: Required[int | float]
    """ Required property """



class UiAction(TypedDict, total=False):
    """ UiAction. """

    type: Required[Literal['UiAction']]
    """ Required property """

    uiElement: Required["_UiActionuiElement"]
    """ Required property """

    uiActionType: "_UiActionuiActionType"
    options: Required["_UiActionoptions"]
    """ Required property """



class UiEvent(TypedDict, total=False):
    """ UiEvent. """

    type: Required[Literal['UiEvent']]
    """ Required property """

    uiEventType: Required["_UiEventuiEventType"]
    """ Required property """

    uiElement: Required["_UiEventuiElement"]
    """ Required property """

    slug: str


class UnrealStateUpdate(TypedDict, total=False):
    """ UnrealStateUpdate. """

    type: Required[Literal['UnrealStateUpdate']]
    """ Required property """



class Validator(TypedDict, total=False):
    """ Validator. """

    type: Required[Literal['Validator']]
    """ Required property """

    requestId: Required[str]
    """ Required property """

    validatorId: Required[str]
    """ Required property """



class ValidatorResponse(TypedDict, total=False):
    """ ValidatorResponse. """

    type: Required[Literal['ValidatorResponse']]
    """ Required property """

    requestId: Required[str]
    """ Required property """

    validatorId: Required[str]
    """ Required property """

    password: str
    access: Required["_ValidatorResponseaccess"]
    """ Required property """



class VoiceChatGroupStateChanged(TypedDict, total=False):
    """ VoiceChatGroupStateChanged. """

    type: Required[Literal['VoiceChatGroupStateChanged']]
    """ Required property """

    groupId: Required[str]
    """ Required property """

    videoSharingUrl: Required[str]
    """ Required property """



class VoiceChatUserGroupChanged(TypedDict, total=False):
    """ VoiceChatUserGroupChanged. """

    type: Required[Literal['VoiceChatUserGroupChanged']]
    """ Required property """

    userId: Required[str]
    """ Required property """

    groupId: Required[str]
    """ Required property """



class VoiceChatUserStateChanged(TypedDict, total=False):
    """ VoiceChatUserStateChanged. """

    type: Required[Literal['VoiceChatUserStateChanged']]
    """ Required property """

    userId: Required[str]
    """ Required property """

    isSpeaking: Required[bool]
    """ Required property """

    isMuted: Required[bool]
    """ Required property """

    isPresenter: bool
    isVideoSharing: Required[bool]
    """ Required property """



class WebRtcStreamingStats(TypedDict, total=False):
    """ WebRtcStreamingStats. """

    type: Required[Literal['WebRtcStreamingStats']]
    """ Required property """

    data: Required["StreamingStats"]
    """
    StreamingStats.

    Required property
    """



_ActionElementEventevent = Literal['click'] | Literal['change'] | Literal['open'] | Literal['close']
_ACTIONELEMENTEVENTEVENT_CLICK: Literal['click'] = "click"
"""The values for the '_ActionElementEventevent' enum"""
_ACTIONELEMENTEVENTEVENT_CHANGE: Literal['change'] = "change"
"""The values for the '_ActionElementEventevent' enum"""
_ACTIONELEMENTEVENTEVENT_OPEN: Literal['open'] = "open"
"""The values for the '_ActionElementEventevent' enum"""
_ACTIONELEMENTEVENTEVENT_CLOSE: Literal['close'] = "close"
"""The values for the '_ActionElementEventevent' enum"""



class _ActionElementStatusoptions(TypedDict, total=False):
    items: list[str]
    open: bool


class _ActionElementsInfoelementsitem(TypedDict, total=False):
    actionElementId: Required[str]
    """ Required property """

    value: Required[str]
    """ Required property """

    hidden: bool
    options: "_ActionElementsInfoelementsitemoptions"


class _ActionElementsInfoelementsitemoptions(TypedDict, total=False):
    items: list[str]
    open: bool


_ActivateMovementTypemovementType = Literal['walk'] | Literal['fly'] | Literal['hover']
_ACTIVATEMOVEMENTTYPEMOVEMENTTYPE_WALK: Literal['walk'] = "walk"
"""The values for the '_ActivateMovementTypemovementType' enum"""
_ACTIVATEMOVEMENTTYPEMOVEMENTTYPE_FLY: Literal['fly'] = "fly"
"""The values for the '_ActivateMovementTypemovementType' enum"""
_ACTIVATEMOVEMENTTYPEMOVEMENTTYPE_HOVER: Literal['hover'] = "hover"
"""The values for the '_ActivateMovementTypemovementType' enum"""



_Configitem = Union["UiAction", "ReceivedChatMessage", "OnChatMessageDeleted", "PerformanceStats", "NearbyPlayers", "PhotonPlayerConnected", "SmartChatAction", "SmartChatEngineReply", "SmartChatSubscriptionUpdate", "SetIsPresenter", "ShareMedia", "EndSession", "ShowBusinessCard", "ActiveRegion", "GameIsReady", "InfoCard", "ActionPanel", "PhotonPlayerDisconnected", "RoomTeleportStart", "RoomTeleportEnd", "ExternalAssetLoadStatus", "TakeScreenshot", "MouseEnterClickableSpot", "MouseExitClickableSpot", "Validator", "CustomMessage", "Poll", "DisplayMap", "PauseMode", "SetPointerScheme", "LoadingLevelStart", "LoadingLevelEnd", "UnrealStateUpdate", "OpenBusinessCardEditor", "HideUi", "EnterRegion", "ExitRegion", "GameQuiz", "AnalyticsEvent", "MediaCaptureAction", "Reaction", "ScreenSharing", "GetScreenSharingStatus", "MovementTypeChanged", "ProductSelected", "ItemAdded", "QuestsInfo", "QuestProgress", "CurrencyChanged", "ActionElementsInfo", "ActionElementStatus", "OnStartAction", "OnStreamIsShown", "UiEvent", "ActivateMovementType", "SendChatMessage", "DeleteMessage", "TimeTravel", "SendEmoji", "DidFakeTouch", "UIElementCoords", "LoadExternalAsset", "WebRtcStreamingStats", "SmartChatUserPrompt", "SmartChatUserAction", "ScreenSize", "TeleportTo", "TeleportPlayer", "PhotoCaptureEvent", "CustomMessage836", "BusinessCard", "EditingBusinessCard", "ValidatorResponse", "ClientInfo", "LanguageSelected", "PollResultSubmitted", "VoiceChatUserStateChanged", "VoiceChatGroupStateChanged", "VoiceChatUserGroupChanged", "MediaCaptureEvent", "Reaction1508", "ScreenSharing1587", "GetScreenSharingStatus6532", "PauseStream", "ResumeStream", "RequestQuestsInfo", "ActionElementEvent"]
"""
Aggregation type: anyOf
Subtype: "UiAction", "ReceivedChatMessage", "OnChatMessageDeleted", "PerformanceStats", "NearbyPlayers", "PhotonPlayerConnected", "SmartChatAction", "SmartChatEngineReply", "SmartChatSubscriptionUpdate", "SetIsPresenter", "ShareMedia", "EndSession", "ShowBusinessCard", "ActiveRegion", "GameIsReady", "InfoCard", "ActionPanel", "PhotonPlayerDisconnected", "RoomTeleportStart", "RoomTeleportEnd", "ExternalAssetLoadStatus", "TakeScreenshot", "MouseEnterClickableSpot", "MouseExitClickableSpot", "Validator", "CustomMessage", "Poll", "DisplayMap", "PauseMode", "SetPointerScheme", "LoadingLevelStart", "LoadingLevelEnd", "UnrealStateUpdate", "OpenBusinessCardEditor", "HideUi", "EnterRegion", "ExitRegion", "GameQuiz", "AnalyticsEvent", "MediaCaptureAction", "Reaction", "ScreenSharing", "GetScreenSharingStatus", "MovementTypeChanged", "ProductSelected", "ItemAdded", "QuestsInfo", "QuestProgress", "CurrencyChanged", "ActionElementsInfo", "ActionElementStatus", "OnStartAction", "OnStreamIsShown", "UiEvent", "ActivateMovementType", "SendChatMessage", "DeleteMessage", "TimeTravel", "SendEmoji", "DidFakeTouch", "UIElementCoords", "LoadExternalAsset", "WebRtcStreamingStats", "SmartChatUserPrompt", "SmartChatUserAction", "ScreenSize", "TeleportTo", "TeleportPlayer", "PhotoCaptureEvent", "CustomMessage836", "BusinessCard", "EditingBusinessCard", "ValidatorResponse", "ClientInfo", "LanguageSelected", "PollResultSubmitted", "VoiceChatUserStateChanged", "VoiceChatGroupStateChanged", "VoiceChatUserGroupChanged", "MediaCaptureEvent", "Reaction1508", "ScreenSharing1587", "GetScreenSharingStatus6532", "PauseStream", "ResumeStream", "RequestQuestsInfo", "ActionElementEvent"
"""



_MediaCaptureActionaction = Literal['start'] | Literal['complete'] | Literal['cancel']
_MEDIACAPTUREACTIONACTION_START: Literal['start'] = "start"
"""The values for the '_MediaCaptureActionaction' enum"""
_MEDIACAPTUREACTIONACTION_COMPLETE: Literal['complete'] = "complete"
"""The values for the '_MediaCaptureActionaction' enum"""
_MEDIACAPTUREACTIONACTION_CANCEL: Literal['cancel'] = "cancel"
"""The values for the '_MediaCaptureActionaction' enum"""



_MediaCaptureActionmediaType = Literal['image'] | Literal['video']
_MEDIACAPTUREACTIONMEDIATYPE_IMAGE: Literal['image'] = "image"
"""The values for the '_MediaCaptureActionmediaType' enum"""
_MEDIACAPTUREACTIONMEDIATYPE_VIDEO: Literal['video'] = "video"
"""The values for the '_MediaCaptureActionmediaType' enum"""



_MediaCaptureEventevent = Literal['start'] | Literal['progress'] | Literal['complete'] | Literal['cancel'] | Literal['error']
_MEDIACAPTUREEVENTEVENT_START: Literal['start'] = "start"
"""The values for the '_MediaCaptureEventevent' enum"""
_MEDIACAPTUREEVENTEVENT_PROGRESS: Literal['progress'] = "progress"
"""The values for the '_MediaCaptureEventevent' enum"""
_MEDIACAPTUREEVENTEVENT_COMPLETE: Literal['complete'] = "complete"
"""The values for the '_MediaCaptureEventevent' enum"""
_MEDIACAPTUREEVENTEVENT_CANCEL: Literal['cancel'] = "cancel"
"""The values for the '_MediaCaptureEventevent' enum"""
_MEDIACAPTUREEVENTEVENT_ERROR: Literal['error'] = "error"
"""The values for the '_MediaCaptureEventevent' enum"""



_MediaCaptureEventmediaType = Literal['image'] | Literal['video']
_MEDIACAPTUREEVENTMEDIATYPE_IMAGE: Literal['image'] = "image"
"""The values for the '_MediaCaptureEventmediaType' enum"""
_MEDIACAPTUREEVENTMEDIATYPE_VIDEO: Literal['video'] = "video"
"""The values for the '_MediaCaptureEventmediaType' enum"""



_MovementTypeChangedmovementType = Literal['Fly'] | Literal['Walk'] | Literal['Hover']
_MOVEMENTTYPECHANGEDMOVEMENTTYPE_FLY: Literal['Fly'] = "Fly"
"""The values for the '_MovementTypeChangedmovementType' enum"""
_MOVEMENTTYPECHANGEDMOVEMENTTYPE_WALK: Literal['Walk'] = "Walk"
"""The values for the '_MovementTypeChangedmovementType' enum"""
_MOVEMENTTYPECHANGEDMOVEMENTTYPE_HOVER: Literal['Hover'] = "Hover"
"""The values for the '_MovementTypeChangedmovementType' enum"""



_PhotoCaptureEventevent = Literal['open'] | Literal['close'] | Literal['cancel'] | Literal['taken']
_PHOTOCAPTUREEVENTEVENT_OPEN: Literal['open'] = "open"
"""The values for the '_PhotoCaptureEventevent' enum"""
_PHOTOCAPTUREEVENTEVENT_CLOSE: Literal['close'] = "close"
"""The values for the '_PhotoCaptureEventevent' enum"""
_PHOTOCAPTUREEVENTEVENT_CANCEL: Literal['cancel'] = "cancel"
"""The values for the '_PhotoCaptureEventevent' enum"""
_PHOTOCAPTUREEVENTEVENT_TAKEN: Literal['taken'] = "taken"
"""The values for the '_PhotoCaptureEventevent' enum"""



class _QuestProgressquest(TypedDict, total=False):
    slug: Required[str]
    """ Required property """

    state: Required["_QuestProgressqueststate"]
    """ Required property """

    currencyCollectedAmount: Required[int | float]
    """ Required property """

    currencyNeededAmount: Required[int | float]
    """ Required property """



_QuestProgressqueststate = Literal['Active'] | Literal['Completed'] | Literal['NotStarted']
_QUESTPROGRESSQUESTSTATE_ACTIVE: Literal['Active'] = "Active"
"""The values for the '_QuestProgressqueststate' enum"""
_QUESTPROGRESSQUESTSTATE_COMPLETED: Literal['Completed'] = "Completed"
"""The values for the '_QuestProgressqueststate' enum"""
_QUESTPROGRESSQUESTSTATE_NOTSTARTED: Literal['NotStarted'] = "NotStarted"
"""The values for the '_QuestProgressqueststate' enum"""



class _QuestsInfoquestsitem(TypedDict, total=False):
    slug: Required[str]
    """ Required property """

    state: Required["_QuestsInfoquestsitemstate"]
    """ Required property """

    currencyCollectedAmount: Required[int | float]
    """ Required property """

    currencyNeededAmount: Required[int | float]
    """ Required property """



_QuestsInfoquestsitemstate = Literal['Active'] | Literal['Completed'] | Literal['NotStarted']
_QUESTSINFOQUESTSITEMSTATE_ACTIVE: Literal['Active'] = "Active"
"""The values for the '_QuestsInfoquestsitemstate' enum"""
_QUESTSINFOQUESTSITEMSTATE_COMPLETED: Literal['Completed'] = "Completed"
"""The values for the '_QuestsInfoquestsitemstate' enum"""
_QUESTSINFOQUESTSITEMSTATE_NOTSTARTED: Literal['NotStarted'] = "NotStarted"
"""The values for the '_QuestsInfoquestsitemstate' enum"""



_SetPointerSchemescheme = Literal[0] | Literal[1] | Literal[2]
_SETPOINTERSCHEMESCHEME_0: Literal[0] = 0
"""The values for the '_SetPointerSchemescheme' enum"""
_SETPOINTERSCHEMESCHEME_1: Literal[1] = 1
"""The values for the '_SetPointerSchemescheme' enum"""
_SETPOINTERSCHEMESCHEME_2: Literal[2] = 2
"""The values for the '_SetPointerSchemescheme' enum"""



_ShareMediamediaType = Literal['video'] | Literal['image']
_SHAREMEDIAMEDIATYPE_VIDEO: Literal['video'] = "video"
"""The values for the '_ShareMediamediaType' enum"""
_SHAREMEDIAMEDIATYPE_IMAGE: Literal['image'] = "image"
"""The values for the '_ShareMediamediaType' enum"""



_SmartChatActionaction = Literal['openChat'] | Literal['closeChat'] | Literal['npcTyping']
_SMARTCHATACTIONACTION_OPENCHAT: Literal['openChat'] = "openChat"
"""The values for the '_SmartChatActionaction' enum"""
_SMARTCHATACTIONACTION_CLOSECHAT: Literal['closeChat'] = "closeChat"
"""The values for the '_SmartChatActionaction' enum"""
_SMARTCHATACTIONACTION_NPCTYPING: Literal['npcTyping'] = "npcTyping"
"""The values for the '_SmartChatActionaction' enum"""



_SmartChatUserActionaction = Literal['openChat'] | Literal['closeChat']
_SMARTCHATUSERACTIONACTION_OPENCHAT: Literal['openChat'] = "openChat"
"""The values for the '_SmartChatUserActionaction' enum"""
_SMARTCHATUSERACTIONACTION_CLOSECHAT: Literal['closeChat'] = "closeChat"
"""The values for the '_SmartChatUserActionaction' enum"""



class _UiActionoptions(TypedDict, total=False):
    slug: str


_UiActionuiActionType = Literal['open'] | Literal['close']
_UIACTIONUIACTIONTYPE_OPEN: Literal['open'] = "open"
"""The values for the '_UiActionuiActionType' enum"""
_UIACTIONUIACTIONTYPE_CLOSE: Literal['close'] = "close"
"""The values for the '_UiActionuiActionType' enum"""



_UiActionuiElement = Literal['actionBar'] | Literal['logo'] | Literal['social'] | Literal['infocard'] | Literal['language'] | Literal['settings'] | Literal['map'] | Literal['popup'] | Literal['profile'] | Literal['cinematicView'] | Literal['photo'] | Literal['videoCapture'] | Literal['mediaShare'] | Literal['ending'] | Literal['screenSharing'] | Literal['videoAvatars'] | Literal['hint'] | Literal['questHint'] | Literal['stats'] | Literal['report'] | Literal['devOptions'] | Literal['presentationBar'] | Literal['fullscreenVideo'] | Literal['forceLandscape'] | Literal['startButton'] | Literal['poll'] | Literal['textChatPreview'] | Literal['walletConnect'] | Literal['quest'] | Literal['actionElements'] | Literal['actionBar/social'] | Literal['actionBar/emojis'] | Literal['actionBar/reactionsBar'] | Literal['actionBar/movements'] | Literal['actionBar/map'] | Literal['actionBar/settings'] | Literal['actionBar/photo'] | Literal['cinematicView/skip'] | Literal['fullscreenVideo/skip'] | Literal['social/chat'] | Literal['social/players'] | Literal['social/playerProfile/:playerId'] | Literal['settings/home'] | Literal['settings/about'] | Literal['settings/video'] | Literal['settings/controls'] | Literal['settings/walletconnect']
_UIACTIONUIELEMENT_ACTIONBAR: Literal['actionBar'] = "actionBar"
"""The values for the '_UiActionuiElement' enum"""
_UIACTIONUIELEMENT_LOGO: Literal['logo'] = "logo"
"""The values for the '_UiActionuiElement' enum"""
_UIACTIONUIELEMENT_SOCIAL: Literal['social'] = "social"
"""The values for the '_UiActionuiElement' enum"""
_UIACTIONUIELEMENT_INFOCARD: Literal['infocard'] = "infocard"
"""The values for the '_UiActionuiElement' enum"""
_UIACTIONUIELEMENT_LANGUAGE: Literal['language'] = "language"
"""The values for the '_UiActionuiElement' enum"""
_UIACTIONUIELEMENT_SETTINGS: Literal['settings'] = "settings"
"""The values for the '_UiActionuiElement' enum"""
_UIACTIONUIELEMENT_MAP: Literal['map'] = "map"
"""The values for the '_UiActionuiElement' enum"""
_UIACTIONUIELEMENT_POPUP: Literal['popup'] = "popup"
"""The values for the '_UiActionuiElement' enum"""
_UIACTIONUIELEMENT_PROFILE: Literal['profile'] = "profile"
"""The values for the '_UiActionuiElement' enum"""
_UIACTIONUIELEMENT_CINEMATICVIEW: Literal['cinematicView'] = "cinematicView"
"""The values for the '_UiActionuiElement' enum"""
_UIACTIONUIELEMENT_PHOTO: Literal['photo'] = "photo"
"""The values for the '_UiActionuiElement' enum"""
_UIACTIONUIELEMENT_VIDEOCAPTURE: Literal['videoCapture'] = "videoCapture"
"""The values for the '_UiActionuiElement' enum"""
_UIACTIONUIELEMENT_MEDIASHARE: Literal['mediaShare'] = "mediaShare"
"""The values for the '_UiActionuiElement' enum"""
_UIACTIONUIELEMENT_ENDING: Literal['ending'] = "ending"
"""The values for the '_UiActionuiElement' enum"""
_UIACTIONUIELEMENT_SCREENSHARING: Literal['screenSharing'] = "screenSharing"
"""The values for the '_UiActionuiElement' enum"""
_UIACTIONUIELEMENT_VIDEOAVATARS: Literal['videoAvatars'] = "videoAvatars"
"""The values for the '_UiActionuiElement' enum"""
_UIACTIONUIELEMENT_HINT: Literal['hint'] = "hint"
"""The values for the '_UiActionuiElement' enum"""
_UIACTIONUIELEMENT_QUESTHINT: Literal['questHint'] = "questHint"
"""The values for the '_UiActionuiElement' enum"""
_UIACTIONUIELEMENT_STATS: Literal['stats'] = "stats"
"""The values for the '_UiActionuiElement' enum"""
_UIACTIONUIELEMENT_REPORT: Literal['report'] = "report"
"""The values for the '_UiActionuiElement' enum"""
_UIACTIONUIELEMENT_DEVOPTIONS: Literal['devOptions'] = "devOptions"
"""The values for the '_UiActionuiElement' enum"""
_UIACTIONUIELEMENT_PRESENTATIONBAR: Literal['presentationBar'] = "presentationBar"
"""The values for the '_UiActionuiElement' enum"""
_UIACTIONUIELEMENT_FULLSCREENVIDEO: Literal['fullscreenVideo'] = "fullscreenVideo"
"""The values for the '_UiActionuiElement' enum"""
_UIACTIONUIELEMENT_FORCELANDSCAPE: Literal['forceLandscape'] = "forceLandscape"
"""The values for the '_UiActionuiElement' enum"""
_UIACTIONUIELEMENT_STARTBUTTON: Literal['startButton'] = "startButton"
"""The values for the '_UiActionuiElement' enum"""
_UIACTIONUIELEMENT_POLL: Literal['poll'] = "poll"
"""The values for the '_UiActionuiElement' enum"""
_UIACTIONUIELEMENT_TEXTCHATPREVIEW: Literal['textChatPreview'] = "textChatPreview"
"""The values for the '_UiActionuiElement' enum"""
_UIACTIONUIELEMENT_WALLETCONNECT: Literal['walletConnect'] = "walletConnect"
"""The values for the '_UiActionuiElement' enum"""
_UIACTIONUIELEMENT_QUEST: Literal['quest'] = "quest"
"""The values for the '_UiActionuiElement' enum"""
_UIACTIONUIELEMENT_ACTIONELEMENTS: Literal['actionElements'] = "actionElements"
"""The values for the '_UiActionuiElement' enum"""
_UIACTIONUIELEMENT_ACTIONBAR_SOLIDUS_SOCIAL: Literal['actionBar/social'] = "actionBar/social"
"""The values for the '_UiActionuiElement' enum"""
_UIACTIONUIELEMENT_ACTIONBAR_SOLIDUS_EMOJIS: Literal['actionBar/emojis'] = "actionBar/emojis"
"""The values for the '_UiActionuiElement' enum"""
_UIACTIONUIELEMENT_ACTIONBAR_SOLIDUS_REACTIONSBAR: Literal['actionBar/reactionsBar'] = "actionBar/reactionsBar"
"""The values for the '_UiActionuiElement' enum"""
_UIACTIONUIELEMENT_ACTIONBAR_SOLIDUS_MOVEMENTS: Literal['actionBar/movements'] = "actionBar/movements"
"""The values for the '_UiActionuiElement' enum"""
_UIACTIONUIELEMENT_ACTIONBAR_SOLIDUS_MAP: Literal['actionBar/map'] = "actionBar/map"
"""The values for the '_UiActionuiElement' enum"""
_UIACTIONUIELEMENT_ACTIONBAR_SOLIDUS_SETTINGS: Literal['actionBar/settings'] = "actionBar/settings"
"""The values for the '_UiActionuiElement' enum"""
_UIACTIONUIELEMENT_ACTIONBAR_SOLIDUS_PHOTO: Literal['actionBar/photo'] = "actionBar/photo"
"""The values for the '_UiActionuiElement' enum"""
_UIACTIONUIELEMENT_CINEMATICVIEW_SOLIDUS_SKIP: Literal['cinematicView/skip'] = "cinematicView/skip"
"""The values for the '_UiActionuiElement' enum"""
_UIACTIONUIELEMENT_FULLSCREENVIDEO_SOLIDUS_SKIP: Literal['fullscreenVideo/skip'] = "fullscreenVideo/skip"
"""The values for the '_UiActionuiElement' enum"""
_UIACTIONUIELEMENT_SOCIAL_SOLIDUS_CHAT: Literal['social/chat'] = "social/chat"
"""The values for the '_UiActionuiElement' enum"""
_UIACTIONUIELEMENT_SOCIAL_SOLIDUS_PLAYERS: Literal['social/players'] = "social/players"
"""The values for the '_UiActionuiElement' enum"""
_UIACTIONUIELEMENT_SOCIAL_SOLIDUS_PLAYERPROFILE_SOLIDUS__COLON_PLAYERID: Literal['social/playerProfile/:playerId'] = "social/playerProfile/:playerId"
"""The values for the '_UiActionuiElement' enum"""
_UIACTIONUIELEMENT_SETTINGS_SOLIDUS_HOME: Literal['settings/home'] = "settings/home"
"""The values for the '_UiActionuiElement' enum"""
_UIACTIONUIELEMENT_SETTINGS_SOLIDUS_ABOUT: Literal['settings/about'] = "settings/about"
"""The values for the '_UiActionuiElement' enum"""
_UIACTIONUIELEMENT_SETTINGS_SOLIDUS_VIDEO: Literal['settings/video'] = "settings/video"
"""The values for the '_UiActionuiElement' enum"""
_UIACTIONUIELEMENT_SETTINGS_SOLIDUS_CONTROLS: Literal['settings/controls'] = "settings/controls"
"""The values for the '_UiActionuiElement' enum"""
_UIACTIONUIELEMENT_SETTINGS_SOLIDUS_WALLETCONNECT: Literal['settings/walletconnect'] = "settings/walletconnect"
"""The values for the '_UiActionuiElement' enum"""



_UiEventuiElement = Literal['actionBar'] | Literal['logo'] | Literal['social'] | Literal['infocard'] | Literal['language'] | Literal['settings'] | Literal['map'] | Literal['popup'] | Literal['profile'] | Literal['cinematicView'] | Literal['photo'] | Literal['videoCapture'] | Literal['mediaShare'] | Literal['ending'] | Literal['screenSharing'] | Literal['videoAvatars'] | Literal['hint'] | Literal['questHint'] | Literal['stats'] | Literal['report'] | Literal['devOptions'] | Literal['presentationBar'] | Literal['fullscreenVideo'] | Literal['forceLandscape'] | Literal['startButton'] | Literal['poll'] | Literal['textChatPreview'] | Literal['walletConnect'] | Literal['quest'] | Literal['actionElements']
_UIEVENTUIELEMENT_ACTIONBAR: Literal['actionBar'] = "actionBar"
"""The values for the '_UiEventuiElement' enum"""
_UIEVENTUIELEMENT_LOGO: Literal['logo'] = "logo"
"""The values for the '_UiEventuiElement' enum"""
_UIEVENTUIELEMENT_SOCIAL: Literal['social'] = "social"
"""The values for the '_UiEventuiElement' enum"""
_UIEVENTUIELEMENT_INFOCARD: Literal['infocard'] = "infocard"
"""The values for the '_UiEventuiElement' enum"""
_UIEVENTUIELEMENT_LANGUAGE: Literal['language'] = "language"
"""The values for the '_UiEventuiElement' enum"""
_UIEVENTUIELEMENT_SETTINGS: Literal['settings'] = "settings"
"""The values for the '_UiEventuiElement' enum"""
_UIEVENTUIELEMENT_MAP: Literal['map'] = "map"
"""The values for the '_UiEventuiElement' enum"""
_UIEVENTUIELEMENT_POPUP: Literal['popup'] = "popup"
"""The values for the '_UiEventuiElement' enum"""
_UIEVENTUIELEMENT_PROFILE: Literal['profile'] = "profile"
"""The values for the '_UiEventuiElement' enum"""
_UIEVENTUIELEMENT_CINEMATICVIEW: Literal['cinematicView'] = "cinematicView"
"""The values for the '_UiEventuiElement' enum"""
_UIEVENTUIELEMENT_PHOTO: Literal['photo'] = "photo"
"""The values for the '_UiEventuiElement' enum"""
_UIEVENTUIELEMENT_VIDEOCAPTURE: Literal['videoCapture'] = "videoCapture"
"""The values for the '_UiEventuiElement' enum"""
_UIEVENTUIELEMENT_MEDIASHARE: Literal['mediaShare'] = "mediaShare"
"""The values for the '_UiEventuiElement' enum"""
_UIEVENTUIELEMENT_ENDING: Literal['ending'] = "ending"
"""The values for the '_UiEventuiElement' enum"""
_UIEVENTUIELEMENT_SCREENSHARING: Literal['screenSharing'] = "screenSharing"
"""The values for the '_UiEventuiElement' enum"""
_UIEVENTUIELEMENT_VIDEOAVATARS: Literal['videoAvatars'] = "videoAvatars"
"""The values for the '_UiEventuiElement' enum"""
_UIEVENTUIELEMENT_HINT: Literal['hint'] = "hint"
"""The values for the '_UiEventuiElement' enum"""
_UIEVENTUIELEMENT_QUESTHINT: Literal['questHint'] = "questHint"
"""The values for the '_UiEventuiElement' enum"""
_UIEVENTUIELEMENT_STATS: Literal['stats'] = "stats"
"""The values for the '_UiEventuiElement' enum"""
_UIEVENTUIELEMENT_REPORT: Literal['report'] = "report"
"""The values for the '_UiEventuiElement' enum"""
_UIEVENTUIELEMENT_DEVOPTIONS: Literal['devOptions'] = "devOptions"
"""The values for the '_UiEventuiElement' enum"""
_UIEVENTUIELEMENT_PRESENTATIONBAR: Literal['presentationBar'] = "presentationBar"
"""The values for the '_UiEventuiElement' enum"""
_UIEVENTUIELEMENT_FULLSCREENVIDEO: Literal['fullscreenVideo'] = "fullscreenVideo"
"""The values for the '_UiEventuiElement' enum"""
_UIEVENTUIELEMENT_FORCELANDSCAPE: Literal['forceLandscape'] = "forceLandscape"
"""The values for the '_UiEventuiElement' enum"""
_UIEVENTUIELEMENT_STARTBUTTON: Literal['startButton'] = "startButton"
"""The values for the '_UiEventuiElement' enum"""
_UIEVENTUIELEMENT_POLL: Literal['poll'] = "poll"
"""The values for the '_UiEventuiElement' enum"""
_UIEVENTUIELEMENT_TEXTCHATPREVIEW: Literal['textChatPreview'] = "textChatPreview"
"""The values for the '_UiEventuiElement' enum"""
_UIEVENTUIELEMENT_WALLETCONNECT: Literal['walletConnect'] = "walletConnect"
"""The values for the '_UiEventuiElement' enum"""
_UIEVENTUIELEMENT_QUEST: Literal['quest'] = "quest"
"""The values for the '_UiEventuiElement' enum"""
_UIEVENTUIELEMENT_ACTIONELEMENTS: Literal['actionElements'] = "actionElements"
"""The values for the '_UiEventuiElement' enum"""



_UiEventuiEventType = Literal['onOpen'] | Literal['onClose']
_UIEVENTUIEVENTTYPE_ONOPEN: Literal['onOpen'] = "onOpen"
"""The values for the '_UiEventuiEventType' enum"""
_UIEVENTUIEVENTTYPE_ONCLOSE: Literal['onClose'] = "onClose"
"""The values for the '_UiEventuiEventType' enum"""



_ValidatorResponseaccess = Literal['granted'] | Literal['denied'] | Literal['validation']
_VALIDATORRESPONSEACCESS_GRANTED: Literal['granted'] = "granted"
"""The values for the '_ValidatorResponseaccess' enum"""
_VALIDATORRESPONSEACCESS_DENIED: Literal['denied'] = "denied"
"""The values for the '_ValidatorResponseaccess' enum"""
_VALIDATORRESPONSEACCESS_VALIDATION: Literal['validation'] = "validation"
"""The values for the '_ValidatorResponseaccess' enum"""

