📁 文档基本结构
latex
% 指定编译引擎（放在文件最开头）
% !TEX program = xelatex

% 文档类声明（使用学校模板或标准类）
\documentclass{nkuthesis}  % 使用学校提供的模板
% 或者使用标准类：
% \documentclass[12pt,a4paper]{article}  % 普通文章
% \documentclass[12pt,a4paper]{report}   % 支持章(chapter)的报告

% ========== 导言区：加载宏包和设置 ==========
\usepackage[UTF8]{ctex}      % 中文支持（如果用标准类需要）
\usepackage{graphicx}        % 插入图片
\usepackage{booktabs}        % 三线表
\usepackage{amsmath,amssymb} % 数学公式
\usepackage{subcaption}      % 子图
\usepackage{url}             % URL链接
\usepackage{hyperref}        % 超链接（通常最后加载）

% 参考文献设置（根据模板要求选择一种）
\usepackage[backend=biber, style=gb7714-2015]{biblatex}  % 中文参考文献格式
\addbibresource{ref.bib}     % 导入参考文献数据库

% 页面设置（如需要手动调整）
\usepackage{geometry}
\geometry{left=3cm, right=2.5cm, top=2.5cm, bottom=2.5cm}

% 行距设置
\linespread{1.5}  % 1.5倍行距

% ========== 文档开始 ==========
\begin{document}

% ---------- 前置部分（罗马页码）----------
\pagenumbering{Roman}

% 封面（通常由模板的\maketitle命令生成）
\maketitle

% 原创性声明（通常单独一个文件）
\include{declaration}  % 或者直接输入内容

% 摘要
\begin{abstract}
这里是中文摘要内容...
\keywords{关键词1；关键词2；关键词3}
\end{abstract}

\begin{abstract*}
This is English abstract...
\keywords*{Keyword1; Keyword2; Keyword3}
\end{abstract*}

% 目录
\tableofcontents

% 图表目录（如需要）
\listoffigures    % 图目录
\listoftables     % 表目录

% ---------- 正文部分（阿拉伯页码）----------
\pagenumbering{arabic}
\setcounter{page}{1}  % 从第1页开始

% 各章节内容
\include{chapter1}   % 引言
\include{chapter2}   % 相关工作
\include{chapter3}   % 方法
\include{chapter4}   % 实验
\include{chapter5}   % 结论

% ---------- 后置部分 ----------
% 参考文献
\printbibliography  % 如果用biblatex
% 或者
% \bibliographystyle{unsrt}
% \bibliography{ref}

% 附录
\appendix
\include{appendix1}  % 附录A
\include{appendix2}  % 附录B

% 致谢
\begin{acknowledgement}
感谢...
\end{acknowledgement}

\end{document}
📝 章节标题命令
latex
% ========== 章节层级 ==========
% article类（无chapter，适合短论文）
\section{第一章标题}        % 1. 第一章
\subsection{第一节标题}      % 1.1 第一节
\subsubsection{第一小节标题} % 1.1.1 第一小节
\paragraph{段落标题}        % 更小的层级

% report/book类（有chapter，适合长论文/书籍）
\chapter{第一章标题}        % 第一章
\section{第一节标题}        % 1.1 第一节
\subsection{第一小节标题}    % 1.1.1 第一小节

% 不带编号的标题（加*号）
\section*{前言}  % 不编号，也不加入目录

% 手动加入目录（用于带*的标题）
\section*{前言}
\addcontentsline{toc}{section}{前言}  % 手动加入目录
📄 封面设置（常见模板接口）
latex
% ========== 封面信息设置 ==========
\title{南开大学本科生毕业论文\\ 基于深度学习的火灾现场导线熔痕分析}
\title*{Nankai University Bachelor's Thesis \\ Deep Learning Based Analysis of Wire Melt Marks}

\author{邓伟}
\studentid{2213044}
\grade{2022级}
\major{物联网工程}
\department{密码与网络空间安全学院}
\college{密码与网络空间安全学院}
\adviser{赵宏\quad 教授}
\date{2026年6月}

% 关键词
\keywords{火灾调查；导线熔痕；深度学习；UNet；Mask R-CNN}
\keywords*{Fire Investigation; Wire Melt Marks; Deep Learning; U-Net; Mask R-CNN}

% 生成封面
\maketitle
🖼️ 图片插入
latex
% ========== 单张图片 ==========
\begin{figure}[htbp]  % 选项：h(here), t(top), b(bottom), p(page)
    \centering
    \includegraphics[width=0.8\textwidth]{images/figure1.png}
    \caption{这是图片标题}
    \label{fig:example}
\end{figure}

% ========== 两张并排图片 ==========
\begin{figure}[htbp]
    \centering
    \begin{subfigure}[b]{0.45\textwidth}
        \centering
        \includegraphics[width=\textwidth]{images/fig-a.png}
        \caption{一次短路熔痕}
        \label{fig:primary}
    \end{subfigure}
    \hfill  % 添加水平间距
    \begin{subfigure}[b]{0.45\textwidth}
        \centering
        \includegraphics[width=\textwidth]{images/fig-b.png}
        \caption{二次短路熔痕}
        \label{fig:secondary}
    \end{subfigure}
    \caption{导线熔痕微观结构对比}
    \label{fig:comparison}
\end{figure}

% ========== 图片引用 ==========
如图\ref{fig:example}所示...  % 显示为"如图1所示"
📊 表格制作
latex
% ========== 简单表格 ==========
\begin{table}[htbp]
    \centering
    \caption{实验结果对比}
    \label{tab:result}
    \begin{tabular}{|c|c|c|}
        \hline
        方法 & 准确率 & 召回率 \\
        \hline
        U-Net & 0.85 & 0.82 \\
        Mask R-CNN & 0.91 & 0.89 \\
        本文方法 & 0.94 & 0.92 \\
        \hline
    \end{tabular}
\end{table}

% ========== 三线表（推荐） ==========
\begin{table}[htbp]
    \centering
    \caption{实验结果对比（三线表）}
    \label{tab:result2}
    \begin{tabular}{lccc}
        \toprule
        方法 & 准确率 & 召回率 & F1分数 \\
        \midrule
        U-Net & 0.85 & 0.82 & 0.83 \\
        Mask R-CNN & 0.91 & 0.89 & 0.90 \\
        本文方法 & 0.94 & 0.92 & 0.93 \\
        \bottomrule
    \end{tabular}
\end{table}

% ========== 跨页长表格 ==========
\begin{longtable}{ccc}
    \caption{跨页表格示例} \\
    \toprule
    第一列 & 第二列 & 第三列 \\
    \midrule
    \endfirsthead
    
    \multicolumn{3}{c}{续表} \\
    \toprule
    第一列 & 第二列 & 第三列 \\
    \midrule
    \endhead
    
    \bottomrule
    \endfoot
    
    数据1 & 数据2 & 数据3 \\
    数据4 & 数据5 & 数据6 \\
    % ...更多行
\end{longtable}
➗ 数学公式
latex
% ========== 行内公式 ==========
这是行内公式 $E = mc^2$，直接写在文字中。

% ========== 行间公式（编号）==========
\begin{equation}
    \label{eq:einstein}
    E = mc^2
\end{equation}

% ========== 多行公式 ==========
\begin{align}
    \label{eq:multi}
    f(x) &= x^2 + 2x + 1 \\
    g(x) &= \sin x + \cos x
\end{align}

% ========== 分段函数 ==========
\begin{equation}
    \label{eq:piecewise}
    \text{Accuracy} = 
    \begin{cases}
        1, & \text{if prediction is correct} \\
        0, & \text{otherwise}
    \end{cases}
\end{equation}

% ========== 矩阵 ==========
\begin{equation}
    \begin{bmatrix}
        a_{11} & a_{12} \\
        a_{21} & a_{22}
    \end{bmatrix}
\end{equation}
📚 参考文献
latex
% ========== 参考文献数据库 (ref.bib) ==========
% 这是.bib文件的内容示例
@article{zhang2023deep,
    title={基于深度学习的火灾现场导线熔痕识别},
    author={张伟 and 李娜},
    journal={火灾科学},
    volume={42},
    number={3},
    pages={215-223},
    year={2023}
}

@inproceedings{wang2022void,
    title={Void Analysis in Wire Melt Marks Using Deep Learning},
    author={Wang, H. and Chen, L. and Liu, Y.},
    booktitle={2022 International Conference on Fire Safety},
    pages={45-52},
    year={2022}
}

% ========== 在正文中引用 ==========
根据文献~\cite{zhang2023deep}的研究表明...
已有工作~\cite{wang2022void}提出了...

% ========== 多种引用格式 ==========
\cite{zhang2023deep}           % [1]
\citet{zhang2023deep}          % Zhang等人 [1]（作者作为主语）
\citep{zhang2023deep}          % [1]（括号引用）
\cite{zhang2023deep, wang2022void} % [1,2] 多篇引用
🔗 交叉引用
latex
% ========== 添加标签 ==========
\section{研究方法}
\label{sec:method}

\begin{figure}
    \caption{系统架构图}
    \label{fig:architecture}
\end{figure}

\begin{table}
    \caption{实验数据}
    \label{tab:data}
\end{table}

\begin{equation}
    \label{eq:loss}
    Loss = -\sum y \log(\hat{y})
\end{equation}

% ========== 引用标签 ==========
详见第~\ref{sec:method}节...
如图~\ref{fig:architecture}所示...
见表~\ref{tab:data}...
如公式~\ref{eq:loss}所示...

% ========== 设置引用格式（可选）==========
\labelformat{figure}{图~#1}
\labelformat{table}{表~#1}
\labelformat{equation}{公式~#1}
\labelformat{section}{第~#1~节}
📌 列表环境
latex
% ========== 无序列表 ==========
\begin{itemize}
    \item 第一项
    \item 第二项
    \item 第三项
\end{itemize}

% ========== 有序列表 ==========
\begin{enumerate}
    \item 第一步
    \item 第二步
    \item 第三步
\end{enumerate}

% ========== 描述列表 ==========
\begin{description}
    \item[U-Net] 用于图像分割的卷积网络
    \item[Mask R-CNN] 用于实例分割的网络
\end{description}
✨ 常用格式
latex
% ========== 字体样式 ==========
\textbf{粗体}
\textit{斜体}
\underline{下划线}
\texttt{等宽字体}
{\small 小号字} {\large 大号字} {\huge 超大号字}

% ========== 脚注 ==========
这是正文\footnote{这是脚注内容}。

% ========== 换行与空格 ==========
第一行\\
第二行  % \\ 换行

\quad  % 一个汉字的空格
\qquad % 两个汉字的空格
\,     % 小空格
\space % 普通空格

% ========== 水平线 ==========
\hline           % 横线（表格中）
\rule{width}{thickness}  % 自定义横线
\rule{\textwidth}{0.5pt} % 贯穿页面的横线
🚀 编译命令说明
latex
% ========== 文件开头指定编译器 ==========
% !TEX program = xelatex  % 最常用，支持中文
% !TEX program = pdflatex % 传统编译，中文支持较差
% !TEX program = lualatex % 较新，支持中文

% ========== 完整编译流程（含参考文献）==========
% 第一次： xelatex main.tex
% 第二次： biber main     （生成参考文献）
% 第三次： xelatex main.tex
% 第四次： xelatex main.tex （更新交叉引用）

% Overleaf中点击"Recompile"会自动处理这一切
🎯 实用小技巧
latex
% ========== 注释 ==========
% 这是单行注释（不会编译）

\begin{comment}
这是多行注释
可以写很多内容
都不会被编译
\end{comment}

% ========== 导入其他文件 ==========
\include{chapter1}   % 在新的一页开始
\input{section1}     % 直接插入，不分页

% ========== 强制换页 ==========
\newpage
\clearpage  % 强制刷新所有浮动体并换页

% ========== 调试辅助 ==========
\usepackage{lipsum}  % 生成假文
\lipsum[1-3]         % 输出3段拉丁文假文
📋 毕业论文常见错误及解决
错误提示	可能原因	解决方法
! LaTeX Error: File not found	文件路径错误	检查文件名和路径是否正确
! Undefined control sequence	命令拼写错误	检查命令是否正确，是否缺少宏包
! Missing $ inserted	数学公式缺少$符号	检查数学内容是否在$...$或equation内
! Citation undefined	参考文献未编译	运行biber/重新编译
! Overfull \hbox	内容超出页边距	使用\sloppy或手动换行