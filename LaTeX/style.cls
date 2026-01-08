\LoadClass[a4paper,11pt]{book}
\def\version{0.1.0}

\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{style}[2025/01/08 \version]

\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{hyperref}
\usepackage{graphicx}
% Use for translations examples
\usepackage{longtable}
\usepackage{booktabs}

% For customizing titles
\usepackage{titlesec}

% Check for an update of the package
\usepackage[provide=*,breton]{babel}

\renewcommand{\thepart}{\Alph{part}}

% Remove all paragraph indentation
\setlength{\parindent}{0pt}
\setlength{\parskip}{6pt plus 2pt minus 1pt}

\makeatletter

% Customize part titles
\def\@endpart{%
  \vskip 30\p@  % Reduced spacing after part title
  % Don't add \newpage here - allow content to continue
}

% Make chapters start on any page (not just odd pages)
\renewcommand\chapter{%
  \if@openright\clearpage\else\cleardoublepage\fi
  \thispagestyle{plain}%
  \global\@topnum\z@
  \@afterindentfalse
  \secdef\@chapter\@schapter
}
\makeatother

% Tightlist command to avoid errors from pandoc
\def\tightlist{}

% Todo:
% - Look for a more compact layout (wider textwidth, less spaces between chapters and parts, maybe?)