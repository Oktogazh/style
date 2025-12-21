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

\usepackage[breton]{babel}

\newcounter{subchapterusage}

\makeatletter
\let\latex@@thechapter\thechapter
\@addtoreset{chapter}{subchapterusage}% Reset the chapter counter if subchapterusage is stepped

\newcommand{\PrepareForSubchapterUsage}{%
  \xdef\chapvalue{\number\value{chapter}}
  \stepcounter{subchapterusage}%
  \renewcommand{\thechapter}{\chapvalue.\latex@@thechapter}
}

\newcommand{\RestoreToChapterUsage}{%
  \setcounter{chapter}{\chapvalue}
  \renewcommand{\thechapter}{\latex@@thechapter}
}

\makeatother