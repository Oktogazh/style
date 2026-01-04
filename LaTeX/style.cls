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
\usepackage[provide=*,breton]{babel}

\renewcommand{\thepart}{\Alph{part}}

% Remove all paragraph indentation
\setlength{\parindent}{0pt}
\setlength{\parskip}{6pt plus 2pt minus 1pt}

\makeatother
\def\tightlist{}

% Todo:
% - remove category tags (Rummad: ...)
% - style the parts and chapters
% - style the bibliography
% - find bugs