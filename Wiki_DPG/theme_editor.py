from dearpygui.dearpygui import * 

def create_theme():
    with theme() as theme_id:
        add_theme_color(mvThemeCol_Text                   , (1.00 * 255, 1.00 * 255, 1.00 * 255, 1.00 * 255))
        add_theme_color(mvThemeCol_TextDisabled           , (0.50 * 255, 0.50 * 255, 0.50 * 255, 1.00 * 255))
        add_theme_color(mvThemeCol_WindowBg               , (0.06 * 255, 0.06 * 255, 0.06 * 255, 0.94 * 255))
        add_theme_color(mvThemeCol_ChildBg                , (0.00 * 255, 0.00 * 255, 0.00 * 255, 0.00 * 255))
        add_theme_color(mvThemeCol_PopupBg                , (0.08 * 255, 0.08 * 255, 0.08 * 255, 0.94 * 255))

        add_theme_color(mvThemeCol_Border                 , (0.43 * 255, 0.43 * 255, 0.50 * 255, 0.50 * 255))
        add_theme_color(mvThemeCol_BorderShadow           , (0.00 * 255, 0.00 * 255, 0.00 * 255, 0.00 * 255))

        add_theme_color(mvThemeCol_FrameBg                , (0.16 * 255, 0.29 * 255, 0.48 * 255, 0.54 * 255))
        add_theme_color(mvThemeCol_FrameBgHovered         , (0.26 * 255, 0.59 * 255, 0.98 * 255, 0.40 * 255))
        add_theme_color(mvThemeCol_FrameBgActive          , (0.26 * 255, 0.59 * 255, 0.98 * 255, 0.67 * 255))

        add_theme_color(mvThemeCol_TitleBg                , (0.04 * 255, 0.04 * 255, 0.04 * 255, 1.00 * 255))
        add_theme_color(mvThemeCol_TitleBgActive          , (0.16 * 255, 0.29 * 255, 0.48 * 255, 1.00 * 255))
        add_theme_color(mvThemeCol_TitleBgCollapsed       , (0.00 * 255, 0.00 * 255, 0.00 * 255, 0.51 * 255))
        add_theme_color(mvThemeCol_MenuBarBg              , (0.14 * 255, 0.14 * 255, 0.14 * 255, 1.00 * 255))

        add_theme_color(mvThemeCol_ScrollbarBg            , (0.02 * 255, 0.02 * 255, 0.02 * 255, 0.53 * 255))
        add_theme_color(mvThemeCol_ScrollbarGrab          , (0.31 * 255, 0.31 * 255, 0.31 * 255, 1.00 * 255))
        add_theme_color(mvThemeCol_ScrollbarGrabHovered   , (0.41 * 255, 0.41 * 255, 0.41 * 255, 1.00 * 255))
        add_theme_color(mvThemeCol_ScrollbarGrabActive    , (0.51 * 255, 0.51 * 255, 0.51 * 255, 1.00 * 255))

        add_theme_color(mvThemeCol_CheckMark              , (0.26 * 255, 0.59 * 255, 0.98 * 255, 1.00 * 255))
        add_theme_color(mvThemeCol_SliderGrab             , (0.24 * 255, 0.52 * 255, 0.88 * 255, 1.00 * 255))
        add_theme_color(mvThemeCol_SliderGrabActive       , (0.26 * 255, 0.59 * 255, 0.98 * 255, 1.00 * 255))

        add_theme_color(mvThemeCol_Button                 , (0.26 * 255, 0.59 * 255, 0.98 * 255, 0.40 * 255))
        add_theme_color(mvThemeCol_ButtonHovered          , (0.26 * 255, 0.59 * 255, 0.98 * 255, 1.00 * 255))
        add_theme_color(mvThemeCol_ButtonActive           , (0.06 * 255, 0.53 * 255, 0.98 * 255, 1.00 * 255))

        add_theme_color(mvThemeCol_Header                 , (0.26 * 255, 0.59 * 255, 0.98 * 255, 0.31 * 255))
        add_theme_color(mvThemeCol_HeaderHovered          , (0.26 * 255, 0.59 * 255, 0.98 * 255, 0.80 * 255))
        add_theme_color(mvThemeCol_HeaderActive           , (0.26 * 255, 0.59 * 255, 0.98 * 255, 1.00 * 255))

        add_theme_color(mvThemeCol_Separator              , (0.43 * 255, 0.43 * 255, 0.50 * 255, 0.50 * 255))
        add_theme_color(mvThemeCol_SeparatorHovered       , (0.10 * 255, 0.40 * 255, 0.75 * 255, 0.78 * 255))
        add_theme_color(mvThemeCol_SeparatorActive        , (0.10 * 255, 0.40 * 255, 0.75 * 255, 1.00 * 255))

        add_theme_color(mvThemeCol_ResizeGrip             , (0.26 * 255, 0.59 * 255, 0.98 * 255, 0.20 * 255))
        add_theme_color(mvThemeCol_ResizeGripHovered      , (0.26 * 255, 0.59 * 255, 0.98 * 255, 0.67 * 255))
        add_theme_color(mvThemeCol_ResizeGripActive       , (0.26 * 255, 0.59 * 255, 0.98 * 255, 0.95 * 255))

        add_theme_color(mvThemeCol_Tab                    , (0.18 * 255, 0.35 * 255, 0.58 * 255, 0.86 * 255))
        add_theme_color(mvThemeCol_TabHovered             , (0.26 * 255, 0.59 * 255, 0.98 * 255, 0.80 * 255))
        add_theme_color(mvThemeCol_TabActive              , (0.20 * 255, 0.41 * 255, 0.68 * 255, 1.00 * 255))
        add_theme_color(mvThemeCol_TabUnfocused           , (0.07 * 255, 0.10 * 255, 0.15 * 255, 0.97 * 255))
        add_theme_color(mvThemeCol_TabUnfocusedActive     , (0.14 * 255, 0.26 * 255, 0.42 * 255, 1.00 * 255))
        
        add_theme_color(mvThemeCol_DockingPreview         , (0.26 * 255, 0.59 * 255, 0.98 * 255, 0.70 * 255))
        add_theme_color(mvThemeCol_DockingEmptyBg         , (0.20 * 255, 0.20 * 255, 0.20 * 255, 1.00 * 255))
        
        add_theme_color(mvThemeCol_PlotLines              , (0.61 * 255, 0.61 * 255, 0.61 * 255, 1.00 * 255))
        add_theme_color(mvThemeCol_PlotLinesHovered       , (1.00 * 255, 0.43 * 255, 0.35 * 255, 1.00 * 255))
        add_theme_color(mvThemeCol_PlotHistogram          , (0.90 * 255, 0.70 * 255, 0.00 * 255, 1.00 * 255))
        add_theme_color(mvThemeCol_PlotHistogramHovered   , (1.00 * 255, 0.60 * 255, 0.00 * 255, 1.00 * 255))
        
        add_theme_color(mvThemeCol_TableHeaderBg          , (0.19 * 255, 0.19 * 255, 0.20 * 255, 1.00 * 255))
        add_theme_color(mvThemeCol_TableBorderStrong      , (0.31 * 255, 0.31 * 255, 0.35 * 255, 1.00 * 255))
        add_theme_color(mvThemeCol_TableBorderLight       , (0.23 * 255, 0.23 * 255, 0.25 * 255, 1.00 * 255))
        add_theme_color(mvThemeCol_TableRowBg             , (0.00 * 255, 0.00 * 255, 0.00 * 255, 0.00 * 255))
        add_theme_color(mvThemeCol_TableRowBgAlt          , (1.00 * 255, 1.00 * 255, 1.00 * 255, 0.06 * 255))
        
        add_theme_color(mvThemeCol_TextSelectedBg         , (0.26 * 255, 0.59 * 255, 0.98 * 255, 0.35 * 255))
        add_theme_color(mvThemeCol_DragDropTarget         , (1.00 * 255, 1.00 * 255, 0.00 * 255, 0.90 * 255))
        add_theme_color(mvThemeCol_NavHighlight           , (0.26 * 255, 0.59 * 255, 0.98 * 255, 1.00 * 255))
        
        add_theme_color(mvThemeCol_NavWindowingHighlight  , (1.00 * 255, 1.00 * 255, 1.00 * 255, 0.70 * 255))
        add_theme_color(mvThemeCol_NavWindowingDimBg      , (0.80 * 255, 0.80 * 255, 0.80 * 255, 0.20 * 255))
        add_theme_color(mvThemeCol_ModalWindowDimBg       , (0.80 * 255, 0.80 * 255, 0.80 * 255, 0.35 * 255))
        
        add_theme_color(mvPlotCol_FrameBg                 , (1.00 * 255, 1.00 * 255, 1.00 * 255, 0.07 * 255), category = mvThemeCat_Plots )
        add_theme_color(mvPlotCol_PlotBg                  , (0.00 * 255, 0.00 * 255, 0.00 * 255, 0.50 * 255), category = mvThemeCat_Plots )
        add_theme_color(mvPlotCol_PlotBorder              , (0.43 * 255, 0.43 * 255, 0.50 * 255, 0.50 * 255), category = mvThemeCat_Plots )
        add_theme_color(mvPlotCol_LegendBg                , (0.08 * 255, 0.08 * 255, 0.08 * 255, 0.94 * 255), category = mvThemeCat_Plots )
        add_theme_color(mvPlotCol_LegendBorder            , (0.43 * 255, 0.43 * 255, 0.50 * 255, 0.50 * 255), category = mvThemeCat_Plots )
        add_theme_color(mvPlotCol_LegendText              , (1.00 * 255, 1.00 * 255, 1.00 * 255, 1.00 * 255), category = mvThemeCat_Plots )
        add_theme_color(mvPlotCol_TitleText               , (1.00 * 255, 1.00 * 255, 1.00 * 255, 1.00 * 255), category = mvThemeCat_Plots )
        add_theme_color(mvPlotCol_InlayText               , (1.00 * 255, 1.00 * 255, 1.00 * 255, 1.00 * 255), category = mvThemeCat_Plots )
        add_theme_color(mvPlotCol_XAxis                   , (1.00 * 255, 1.00 * 255, 1.00 * 255, 1.00 * 255), category = mvThemeCat_Plots )
        add_theme_color(mvPlotCol_XAxisGrid               , (1.00 * 255, 1.00 * 255, 1.00 * 255, 0.25 * 255), category = mvThemeCat_Plots )
        add_theme_color(mvPlotCol_YAxis                   , (1.00 * 255, 1.00 * 255, 1.00 * 255, 1.00 * 255), category = mvThemeCat_Plots )
        add_theme_color(mvPlotCol_YAxisGrid               , (1.00 * 255, 1.00 * 255, 1.00 * 255, 0.25 * 255), category = mvThemeCat_Plots )
        add_theme_color(mvPlotCol_YAxis2                  , (1.00 * 255, 1.00 * 255, 1.00 * 255, 1.00 * 255), category = mvThemeCat_Plots )
        add_theme_color(mvPlotCol_YAxisGrid2              , (1.00 * 255, 1.00 * 255, 1.00 * 255, 0.25 * 255), category = mvThemeCat_Plots )
        add_theme_color(mvPlotCol_YAxis3                  , (1.00 * 255, 1.00 * 255, 1.00 * 255, 1.00 * 255), category = mvThemeCat_Plots )
        add_theme_color(mvPlotCol_YAxisGrid3              , (1.00 * 255, 1.00 * 255, 1.00 * 255, 0.25 * 255), category = mvThemeCat_Plots )
        add_theme_color(mvPlotCol_Selection               , (1.00 * 255, 0.60 * 255, 0.00 * 255, 1.00 * 255), category = mvThemeCat_Plots )
        add_theme_color(mvPlotCol_Query                   , (0.00 * 255, 1.00 * 255, 0.44 * 255, 1.00 * 255), category = mvThemeCat_Plots )
        add_theme_color(mvPlotCol_Crosshairs              , (1.00 * 255, 1.00 * 255, 1.00 * 255, 0.50 * 255), category = mvThemeCat_Plots )
        
        add_theme_color(mvNodeCol_NodeBackground          , (50, 50, 50, 255)   , category = mvThemeCat_Nodes )
        add_theme_color(mvNodeCol_NodeBackgroundHovered   , (75, 75, 75, 255)   , category = mvThemeCat_Nodes )
        add_theme_color(mvNodeCol_NodeBackgroundSelected  , (75, 75, 75, 255)   , category = mvThemeCat_Nodes )
        add_theme_color(mvNodeCol_NodeOutline             , (100, 100, 100, 255), category = mvThemeCat_Nodes )
        add_theme_color(mvNodeCol_TitleBar                , (41, 74, 122, 255)  , category = mvThemeCat_Nodes )
        add_theme_color(mvNodeCol_TitleBarHovered         , (66, 150, 250, 255) , category = mvThemeCat_Nodes )
        add_theme_color(mvNodeCol_TitleBarSelected        , (66, 150, 250, 255) , category = mvThemeCat_Nodes )
        add_theme_color(mvNodeCol_Link                    , (61, 133, 224, 200) , category = mvThemeCat_Nodes )
        add_theme_color(mvNodeCol_LinkHovered             , (66, 150, 250, 255) , category = mvThemeCat_Nodes )
        add_theme_color(mvNodeCol_LinkSelected            , (66, 150, 250, 255) , category = mvThemeCat_Nodes )
        add_theme_color(mvNodeCol_Pin                     , (53, 150, 250, 180) , category = mvThemeCat_Nodes )
        add_theme_color(mvNodeCol_PinHovered              , (53, 150, 250, 255) , category = mvThemeCat_Nodes )
        add_theme_color(mvNodeCol_BoxSelector             , (61, 133, 224, 30)  , category = mvThemeCat_Nodes )
        add_theme_color(mvNodeCol_BoxSelectorOutline      , (61, 133, 224, 150) , category = mvThemeCat_Nodes )
        add_theme_color(mvNodeCol_GridBackground          , (40, 40, 50, 200)   , category = mvThemeCat_Nodes )
        add_theme_color(mvNodeCol_GridLine                , (200, 200, 200, 40) , category = mvThemeCat_Nodes )
    return theme_id