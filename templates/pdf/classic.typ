// Classic Resume Template
// Traditional resume style with serif font, conservative colors, generous margins.
// Suitable for executive, traditional, and formal industry roles.

// Read styling parameters from sys_inputs
#let font_family = sys.inputs.at("font_family", default: "EB Garamond")
#let font_size = eval(sys.inputs.at("font_size", default: "11pt"))
#let accent_color = rgb(sys.inputs.at("accent_color", default: "#2B547E"))
#let margin_size = eval(sys.inputs.at("margin", default: "0.75in"))
#let page_size = sys.inputs.at("page_size", default: "us-letter")
#let line_spacing = eval(sys.inputs.at("line_spacing", default: "0.65em"))
#let section_spacing = eval(sys.inputs.at("section_spacing", default: "0.9em"))

// Read resume content
#let resume_content = sys.inputs.at("resume_content", default: "")

// Page setup
#set page(
  paper: page_size,
  margin: (x: margin_size, y: margin_size),
)

// Text defaults
#set text(
  font: font_family,
  size: font_size,
  lang: "en",
  fill: luma(20),
)

// Paragraph settings
#set par(
  leading: line_spacing,
  justify: false,
)

// Heading styles
#show heading.where(level: 1): set text(
  size: 22pt,
  weight: "bold",
  fill: luma(10),
)
#show heading.where(level: 1): set align(center)
#show heading.where(level: 1): set block(below: 0.3em)

#show heading.where(level: 2): it => {
  v(section_spacing)
  block(below: 0.4em)[
    #text(
      size: font_size + 1.5pt,
      weight: "bold",
      fill: accent_color,
    )[#it.body]
    #v(-0.2em)
    #line(length: 100%, stroke: 0.5pt + luma(120))
  ]
}

#show heading.where(level: 3): it => {
  v(0.4em)
  text(
    size: font_size + 0.5pt,
    weight: "bold",
    fill: luma(20),
  )[#it.body]
}

// List styling
#set list(
  indent: 0.3em,
  body-indent: 0.5em,
  marker: text(size: 0.7em)[#sym.diamond.filled],
)

// Link styling
#show link: set text(fill: accent_color)

// Document metadata
#set document(
  title: "Resume",
  date: datetime.today(),
)

// Render the resume content
#eval(resume_content, mode: "markup")
