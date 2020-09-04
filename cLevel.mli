(* CastANet - cLevel.mli *)

(** Annotation levels. *)

type t = [
  | `COLONIZATION   (** Basic annotation level (colonized vs non-colonized). *) 
  | `ARB_VESICLES   (** Intermediate level, with arbuscules and vesicles.    *)
  | `ALL_FEATURES   (** Fully-featured level, with IRH, ERH and hyphopodia.  *)
]
(** Annotation levels. *)

val available_levels : t list
(** List of available annotation levels. *)

val lowest : t
(** Least detailed level of mycorrhiza annotation. *)

val highest : t
(** Most detailed level of mycorrhiza annotation. *)

val others : t -> t * t
(** [other lvl] returns the two other levels than [lvl]. *)

val colors : t -> string list
(** Returns the list of colors at the given level. *)
