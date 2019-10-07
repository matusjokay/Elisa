module Main exposing (main)

import Data.User as User exposing (User)
import Dialog
import Form exposing (Form)
import Form.Validate as Validate exposing (Validation)
import Html exposing (..)
import Html.Attributes exposing (..)
import Html.Events exposing (onClick)
import Http
import Json.Encode as Encode
import Jwt
import Navigation exposing (Location)
import Page.Courses as Courses
import Page.Timetables as Timetables
import Page.Timetables.Timetable as Timetable
import Ports
import Result exposing (Result(..))
import Route exposing (Route(..), parseLocation)
import Task
import Time exposing (Time)
import Util exposing (apiUrl, onClickPreventDefault)
import Views.Alert as Alert
import Views.Form exposing (passwordGroup, textGroup)


type Page
    = NotFound
    | Blank
    | Home
    | Courses Courses.Model
    | Timetables Timetables.Model
    | Timetable Timetable.Model


type alias Flags =
    { token : Maybe String }


type alias Model =
    { page : Page
    , user : Maybe User
    , loginForm : Form () ( String, String )
    , loginError : Maybe Http.Error
    , showLoginDialog : Bool
    }


initialModel : Model
initialModel =
    { page = Blank
    , user = Nothing
    , loginForm = Form.initial [] validateLoginForm
    , loginError = Nothing
    , showLoginDialog = False
    }


init : Flags -> Navigation.Location -> ( Model, Cmd Msg )
init flags location =
    let
        route =
            parseLocation location

        page =
            pageFromRoute route

        checkTokenExpiration =
            case flags.token of
                Just token ->
                    Task.perform (CheckTokenExpiration token) Time.now

                Nothing ->
                    Cmd.none
    in
        ( { initialModel | page = page }
        , Cmd.batch [ checkTokenExpiration, fetchData route ]
        )


validateLoginForm : Validation () ( String, String )
validateLoginForm =
    Validate.map2 (,)
        (Validate.field "username" Validate.string)
        (Validate.field "password" Validate.string)



-- UPDATE


type Msg
    = NewUrl String
    | UrlChange Location
    | DisplayLoginDialog Bool
    | LoginFormMsg Form.Msg
    | HandleAuthentication (Result Http.Error String)
    | CheckTokenExpiration String Time
    | LogOut
    | CoursesMsg Courses.Msg
    | TimetablesMsg Timetables.Msg
    | TimetableMsg Timetable.Msg


update : Msg -> Model -> ( Model, Cmd Msg )
update msg model =
    let
        user =
            model.user

        toPage toModel toMsg subUpdate subMsg subModel =
            let
                ( newModel, newCmd ) =
                    subUpdate subMsg subModel
            in
                ( { model | page = toModel newModel }, Cmd.map toMsg newCmd )
    in
        case ( msg, model.page ) of
            ( NewUrl url, _ ) ->
                ( model, Navigation.newUrl url )

            ( UrlChange location, _ ) ->
                let
                    route =
                        parseLocation location
                in
                    ( { model | page = pageFromRoute route }, fetchData route )

            ( DisplayLoginDialog shouldDisplay, _ ) ->
                let
                    newModel =
                        { model | showLoginDialog = shouldDisplay }
                in
                    if shouldDisplay then
                        ( newModel, Cmd.none )
                    else
                        ( { newModel
                            | loginForm = Form.initial [] validateLoginForm
                            , loginError = Nothing
                          }
                        , Cmd.none
                        )

            ( LoginFormMsg formMsg, _ ) ->
                case ( formMsg, Form.getOutput model.loginForm ) of
                    ( Form.Submit, Just credentials ) ->
                        ( model, login credentials )

                    _ ->
                        let
                            newLoginForm =
                                Form.update validateLoginForm formMsg model.loginForm
                        in
                            ( { model | loginForm = newLoginForm }, Cmd.none )

            ( HandleAuthentication result, _ ) ->
                case result of
                    Ok token ->
                        ( { model
                            | user = User.fromToken token
                            , showLoginDialog = False
                          }
                        , Ports.storeToken token
                        )

                    Err error ->
                        ( { model | loginError = Just error }, Cmd.none )

            ( CheckTokenExpiration token now, _ ) ->
                case Jwt.isExpired now token of
                    Ok False ->
                        ( { model | user = User.fromToken token }, Cmd.none )

                    _ ->
                        ( { model | user = Nothing }, Ports.removeToken () )

            ( LogOut, _ ) ->
                ( { model | user = Nothing }, Ports.removeToken () )

            ( CoursesMsg subMsg, Courses subModel ) ->
                toPage Courses CoursesMsg Courses.update subMsg subModel

            ( TimetablesMsg subMsg, Timetables subModel ) ->
                toPage Timetables TimetablesMsg (Timetables.update user) subMsg subModel

            ( TimetableMsg subMsg, Timetable subModel ) ->
                toPage Timetable TimetableMsg Timetable.update subMsg subModel

            ( _, NotFound ) ->
                -- Disregard incoming messages when we're on the NotFound page.
                ( model, Cmd.none )

            _ ->
                -- Disregard incoming messages that arrived for the wrong page
                ( model, Cmd.none )


pageFromRoute : Route -> Page
pageFromRoute route =
    case route of
        Route.Home ->
            Home

        Route.Timetables ->
            Timetables Timetables.initialModel

        Route.Timetable _ ->
            Timetable Timetable.initialModel

        Route.Courses ->
            Courses Courses.initialModel

        _ ->
            NotFound


topPageRoute : Page -> Route
topPageRoute page =
    case page of
        Home ->
            Route.Home

        Courses _ ->
            Route.Courses

        Timetables _ ->
            Route.Timetables

        Timetable _ ->
            Route.Timetables

        _ ->
            Route.NotFound


fetchData : Route -> Cmd Msg
fetchData route =
    case route of
        Route.Timetables ->
            Cmd.map TimetablesMsg Timetables.getTimetables

        Route.Courses ->
            Cmd.map CoursesMsg Courses.getCourses

        _ ->
            Cmd.none


login : ( String, String ) -> Cmd Msg
login ( username, password ) =
    Encode.object
        [ ( "username", Encode.string username )
        , ( "password", Encode.string password )
        ]
        |> Jwt.authenticate (apiUrl "/api-token-auth/") User.tokenDecoder
        |> Http.send HandleAuthentication



-- SUBSCRIPTIONS


subscriptions : Model -> Sub Msg
subscriptions model =
    case model.page of
        Timetable subModel ->
            Sub.map TimetableMsg (Timetable.subscriptions subModel)

        _ ->
            Sub.none



-- VIEW


view : Model -> Html Msg
view model =
    div []
        [ viewNavbar model
        , Dialog.view <|
            if model.showLoginDialog then
                Just (dialogConfig model)
            else
                Nothing
        , viewPage model
        ]


viewNavbar : Model -> Html Msg
viewNavbar model =
    nav [ class "navbar navbar-default navbar-static-top" ]
        [ div [ class "container" ]
            [ div [ class "navbar-header" ]
                [ button
                    [ type_ "button"
                    , class "navbar-toggle collapsed"
                    , attribute "data-toggle" "collapse"
                    , attribute "data-target" "#navbar-collapse"
                    , attribute "aria-expanded" "false"
                    ]
                    [ span [ class "sr-only" ] [ text "Toggle navigation" ]
                    , span [ class "icon-bar" ] []
                    , span [ class "icon-bar" ] []
                    , span [ class "icon-bar" ] []
                    ]
                , a
                    (class "navbar-brand" :: Route.navigateTo NewUrl Route.Home)
                    [ text "Elisa" ]
                ]
            , div [ id "navbar-collapse", class "collapse navbar-collapse" ]
                [ ul [ class "nav navbar-nav" ]
                    (List.map (viewMenuItem (topPageRoute model.page)) menuItems)
                , viewLogin model.user
                ]
            ]
        ]


type alias MenuItem =
    { text : String
    , route : Route
    }


menuItems : List MenuItem
menuItems =
    [ { text = "Timetables", route = Route.Timetables }
    , { text = "Courses", route = Route.Courses }
    ]


viewMenuItem : Route -> MenuItem -> Html Msg
viewMenuItem topRoute menuItem =
    let
        status =
            if topRoute == menuItem.route then
                "active"
            else
                ""
    in
        li [ class status ]
            [ a (Route.navigateTo NewUrl menuItem.route) [ text menuItem.text ] ]


viewLogin : Maybe User -> Html Msg
viewLogin maybeUser =
    let
        content =
            case maybeUser of
                Just user ->
                    [ li [ class "navbar-text hidden-xs" ]
                        [ text ("Hi " ++ user.username) ]
                    , li []
                        [ a [ href "", onClickPreventDefault LogOut ]
                            [ span [ class "glyphicon glyphicon-log-out" ] []
                            , text " Log out"
                            ]
                        ]
                    ]

                Nothing ->
                    [ li []
                        [ a
                            [ href ""
                            , onClickPreventDefault (DisplayLoginDialog True)
                            ]
                            [ text "Log in" ]
                        ]
                    ]
    in
        ul [ class "nav navbar-nav navbar-right" ] content


viewLoginForm : Form () ( String, String ) -> Html Form.Msg
viewLoginForm form =
    div [ class "form-horizontal" ]
        [ textGroup (text "Username") (Form.getFieldAsString "username" form)
        , passwordGroup (text "Password") (Form.getFieldAsString "password" form)
        ]


dialogConfig : Model -> Dialog.Config Msg
dialogConfig model =
    let
        alert =
            case model.loginError of
                Just error ->
                    Alert.error error

                Nothing ->
                    text ""
    in
        { closeMessage = Just (DisplayLoginDialog False)
        , containerClass = Nothing
        , header = Just (h2 [ class "modal-title" ] [ text "Log in" ])
        , body =
            Just <|
                div []
                    [ alert
                    , Html.map LoginFormMsg (viewLoginForm model.loginForm)
                    ]
        , footer =
            Just <|
                div []
                    [ button
                        [ class "btn btn-default"
                        , onClick (DisplayLoginDialog False)
                        ]
                        [ text "Cancel" ]
                    , button
                        [ class "btn btn-primary"
                        , onClick (LoginFormMsg Form.Submit)
                        ]
                        [ text "Log in" ]
                    ]
        }


viewPage : Model -> Html Msg
viewPage model =
    let
        isUserAdmin =
            -- TODO Differentiate according to user permissions.
            model.user /= Nothing
    in
        case model.page of
            Home ->
                div [ class "container" ] [ h2 [] [ text "Home" ] ]

            Timetables subModel ->
                Html.map TimetablesMsg (Timetables.view isUserAdmin subModel)

            Timetable subModel ->
                Html.map TimetableMsg (Timetable.view isUserAdmin subModel)

            Courses subModel ->
                Html.map CoursesMsg (Courses.view subModel)

            Blank ->
                text "Loading"

            NotFound ->
                div [ class "container" ] [ h2 [] [ text "Not Found" ] ]



-- MAIN


main : Program Flags Model Msg
main =
    Navigation.programWithFlags UrlChange
        { init = init
        , update = update
        , subscriptions = subscriptions
        , view = view
        }
