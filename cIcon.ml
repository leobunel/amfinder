(* CastANet - caN_icon.ml *)

open CExt
open Printf

type icon_type = [ `RGBA | `GREY ]
type icon_size = [ `LARGE | `SMALL ]

let dir = "data"

let build_path_list suf =
  let path chr = Filename.concat dir (sprintf "%c_%s.png" chr suf) in
  List.map (fun chr -> chr, path chr) CAnnot.code_list

module Src = struct
  let import n (c, s) = (c, GdkPixbuf.from_file_at_size ~width:n ~height:n s)
  let import_multiple n = List.map (import n)
  let get_any f = function `SMALL -> f 24 | `LARGE -> f 48
  let get = get_any import
  let get_multiple = get_any import_multiple
end

module type IconSet = sig
  val large : (char * GdkPixbuf.pixbuf) list
  val small : (char * GdkPixbuf.pixbuf) list
end

let generator suf =
  let module M = struct
    let names = build_path_list suf
    let large = Src.get_multiple `LARGE names
    let small = Src.get_multiple `SMALL names
  end in (module M : IconSet)

let m_rgba = generator "rgba" (* Active toggle buttons.   *)
let m_grad = generator "grad" (* Active with confidence.  *)
let m_grey = generator "grey" (* Inactive toggle buttons. *)

let get_size_set typ ico = 
  let open (val ico : IconSet) in
  if typ = `SMALL then small else large

let get_icon_set ?(grad = true) = function
  | `GREY -> m_grey
  | `RGBA -> if grad && CAnnot.is_gradient () then m_grad else m_rgba
 
module Joker = struct
  let rgba = ('*', Filename.concat dir "Joker_rgba.png")
  let large_rgba = snd (Src.get `LARGE rgba)
  let small_rgba = snd (Src.get `SMALL rgba)
  let grey = ('*', Filename.concat dir "Joker_grey.png")
  let large_grey = snd (Src.get `LARGE grey)
  let small_grey = snd (Src.get `SMALL grey)
end

let get_joker typ = function
  | `SMALL -> Joker.(if typ = `RGBA then small_rgba else small_grey)
  | `LARGE -> Joker.(if typ = `RGBA then large_rgba else large_grey)

let get ?grad chr typ fmt =
  if chr = '*' then get_joker typ fmt
  else List.assoc chr (get_size_set fmt (get_icon_set ?grad typ)) 
