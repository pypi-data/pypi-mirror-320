#  Copyright (c) 2024 Ubiterra Corporation. All rights reserved.
#  #
#  This ZoneVu Python SDK software is the property of Ubiterra Corporation.
#  You shall use it only in accordance with the terms of the ZoneVu Service Agreement.
#  #
#  This software is made available on PyPI for download and use. However, it is NOT open source.
#  Unauthorized copying, modification, or distribution of this software is strictly prohibited.
#  #
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
#  INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
#  PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE
#  FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
#  ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
#
#
#
import copy

from ...Zonevu import Zonevu

def main_copy_well_docs(zonevu: Zonevu, src_well_name: str, dst_well_name: str):
    """
    Copy the documents from one well to another
    :param zonevu: Zonevu instance
    :param src_well_name: Name of well that is the source of the documents
    :param dst_well_name: Name of well that is the destination for the documents
    :return:
    """
    well_svc = zonevu.well_service

    src_well = well_svc.get_first_named(src_well_name, True)
    dst_well = well_svc.get_first_named(dst_well_name, True)
    if src_well is None or dst_well is None:
        print(f'Cannot execute copy -- well(s) not found.')
        return

    if len(src_well.documents) == 0:
        print(f'The source well has no documents.')
        return

    doc_svc = zonevu.document_service
    for index, src_doc in enumerate(src_well.documents):
        dst_doc = copy.deepcopy(src_doc)
        dst_doc.id = 0
        dst_doc.owner_id = dst_well.id
        doc_svc.create_document(dst_doc)
        doc_svc.copy_doc(src_doc, dst_doc)