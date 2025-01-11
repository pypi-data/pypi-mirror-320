import pytest
import AutoRPE.UtilsRPE.Inserter as Inserter


def test_replace_variable_exact_match():
    # This is the line of code from NEMO
    fun_in = "znam = 'sye'//'_l'//zchar1   ;   z3d(:,:,:) = sye (:,:,jk,:)   ;   CALL iom_rstput( iter, nitrst, numriw, znam , z3d )"
    # This is the argument that we want to replace and its replacement
    piece_to_replace = "z3d"
    replacement = "REAL(z3d, dp)"
    # This is what the function actually gives
    fun_out = Inserter.replace_variable_exact_match(piece_to_replace, replacement, fun_in)
    # This is what it should give
    solution = "znam = 'sye'//'_l'//zchar1   ;   z3d(:,:,:) = sye (:,:,jk,:)   ;   CALL iom_rstput( iter, nitrst, numriw, znam , REAL(z3d, dp) )"
    assert fun_out == solution


def test_replace_variable_exact_match_2():
    # This is the line of code from NEMO
    fun_in = "CALL iom_rstput( iter, nitrst, numriw, 'sxice' , sxice  )"
    # This is the argument that we want to replace and its replacement
    piece_to_replace = "sxice"
    replacement = "REAL(sxice, dp)"
    # This is what the function actually gives
    fun_out = Inserter.replace_variable_exact_match(piece_to_replace, replacement, fun_in)
    # This is what it should give
    solution = "CALL iom_rstput( iter, nitrst, numriw, 'sxice' , REAL(sxice, dp)  )"
    assert fun_out == solution
