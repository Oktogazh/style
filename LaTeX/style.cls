\LoadClass[a4paper,11pt]{book}
\def\version{0.1.0}

\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{style}[2025/12/21 \version]

\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{hyperref}
\usepackage{graphicx}
% Use for translations examples
\usepackage{longtable}
\usepackage{booktabs}

% Check for an update of the package
\usepackage[breton]{babel}

\renewcommand{\thepart}{\Alph{part}}

\makeatother
\def\tightlist{}

% Todo:
% - fix indentation after first paragraph of section
% - remove the links
% - remove category tags (url{...})
% - style the parts and chapters
% - style the bibliography
% - find bugs